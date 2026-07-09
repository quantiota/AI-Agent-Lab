#!/usr/bin/env python3
"""
email_agent.py — a minimal, AGENT-NATIVE CLI email client.

Built for an autonomous agent, not a human: non-interactive, JSON-only output,
stdlib only (imaplib / smtplib / email). Config comes from ~/.env (EMAIL_*),
the same pattern jh-exec uses for JH_*. Each lab points it at its own mailbox
(e.g. info@microserver01.net), giving that agent its own email identity.

Commands (every one prints JSON to stdout; exit 0 ok, non-zero on error):
  inbox   [--unread] [--limit N]                 list envelopes, newest first
  read    <uid> [--mark-seen]                     one full message (plain-text body)
  send    --to A --subject S --body B [--cc C] [--html]
  reply   <uid> --body B [--all]                  threaded reply (In-Reply-To/References)
  search  "<imap query>" [--limit N]              raw IMAP SEARCH criteria

Config (~/.env or ./.env; real env vars win):
  EMAIL_IMAP_HOST=  EMAIL_IMAP_PORT=993  EMAIL_IMAP_SSL=true
  EMAIL_SMTP_HOST=  EMAIL_SMTP_PORT=587  EMAIL_SMTP_MODE=starttls   # starttls|ssl|plain
  EMAIL_USER=info@microserver01.net      EMAIL_PASS=...
  EMAIL_MAILBOX=INBOX
"""
import argparse
import imaplib
import json
import os
import re
import smtplib
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.utils import formatdate, getaddresses, make_msgid, parseaddr


# ---- config -----------------------------------------------------------------
def load_config():
    env = {}
    for p in (os.path.join(os.getcwd(), ".env"), os.path.join(os.path.expanduser("~"), ".env")):
        try:
            with open(p) as f:
                for line in f:
                    s = line.strip()
                    if s and not s.startswith("#") and "=" in s:
                        k, v = s.split("=", 1)
                        env[k.strip()] = v.strip().strip("\"'")
            break
        except OSError:
            continue

    def g(k):
        v = os.environ.get(k) or env.get(k)
        return v if v not in (None, "") else None

    def _bool(v):
        return None if v is None else v.lower() == "true"

    user = g("EMAIL_USER")
    cfg = {
        "user": user,
        "password": g("EMAIL_PASS"),
        "mailbox": g("EMAIL_MAILBOX") or "INBOX",
        "imap_host": g("EMAIL_IMAP_HOST"),
        "imap_port": int(g("EMAIL_IMAP_PORT")) if g("EMAIL_IMAP_PORT") else None,
        "imap_ssl": _bool(g("EMAIL_IMAP_SSL")),
        "imap_starttls": None,
        "smtp_host": g("EMAIL_SMTP_HOST"),
        "smtp_port": int(g("EMAIL_SMTP_PORT")) if g("EMAIL_SMTP_PORT") else None,
        "smtp_mode": (g("EMAIL_SMTP_MODE") or "").lower() or None,  # ssl|starttls|plain
    }

    # If host isn't fully specified, autodiscover it from the address (Mozilla
    # ISPDB / provider autoconfig / MX-based lookup) so ~/.env needs only USER+PASS.
    if user and (not cfg["imap_host"] or not cfg["smtp_host"]):
        disc = _autodiscover(user)
        if disc:
            i, s = disc
            cfg["imap_host"] = cfg["imap_host"] or i["host"]
            if cfg["imap_port"] is None:
                cfg["imap_port"] = i["port"]
            if cfg["imap_ssl"] is None:
                cfg["imap_ssl"] = i["socket"] == "SSL"
            if cfg["imap_starttls"] is None:
                cfg["imap_starttls"] = i["socket"] == "STARTTLS"
            cfg["smtp_host"] = cfg["smtp_host"] or s["host"]
            if cfg["smtp_port"] is None:
                cfg["smtp_port"] = s["port"]
            if cfg["smtp_mode"] is None:
                cfg["smtp_mode"] = {"SSL": "ssl", "STARTTLS": "starttls", "PLAIN": "plain"}.get(s["socket"], "starttls")

    # final defaults
    cfg["imap_port"] = cfg["imap_port"] or 993
    cfg["imap_ssl"] = True if cfg["imap_ssl"] is None else cfg["imap_ssl"]
    cfg["imap_starttls"] = bool(cfg["imap_starttls"])
    cfg["smtp_port"] = cfg["smtp_port"] or 587
    cfg["smtp_mode"] = cfg["smtp_mode"] or "starttls"
    return cfg


# ---- autodiscovery (Thunderbird-style: ISPDB → autoconfig → MX → ISPDB) ------
_DISC_CACHE = os.path.join(os.path.expanduser("~"), ".email_agent_autoconfig.json")


def _disc_cache(domain, value=None):
    try:
        data = {}
        try:
            with open(_DISC_CACHE) as f:
                data = json.load(f)
        except OSError:
            pass
        if value is None:
            e = data.get(domain)
            return (e["imap"], e["smtp"]) if e else None
        data[domain] = {"imap": value[0], "smtp": value[1]}
        with open(_DISC_CACHE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass
    return None


def _localname(el):
    """Tag without any XML namespace prefix (autoconfig files vary)."""
    return el.tag.rsplit("}", 1)[-1]


def _parse_autoconfig(xml):
    try:
        root = ET.fromstring(xml)
    except Exception:
        return None
    prov = next((el for el in root.iter() if _localname(el) == "emailProvider"), None)
    if prov is None:
        return None

    def pick(server_tag, typ):
        for s in prov.iter():
            if _localname(s) != server_tag or s.get("type") != typ:
                continue
            vals = {_localname(c): (c.text or "").strip() for c in s}
            host, port = vals.get("hostname"), vals.get("port")
            if not host or not (port or "").isdigit():
                continue  # skip malformed entries rather than crash
            return {"host": host, "port": int(port), "socket": (vals.get("socketType") or "SSL").upper()}
        return None

    imap, smtp = pick("incomingServer", "imap"), pick("outgoingServer", "smtp")
    return (imap, smtp) if imap and smtp else None


def _fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "email-agent"})
        with urllib.request.urlopen(req, timeout=6) as r:
            return _parse_autoconfig(r.read())
    except Exception:
        return None


def _mx_domain(domain):
    try:
        with urllib.request.urlopen(f"https://dns.google/resolve?name={domain}&type=MX", timeout=6) as r:
            ans = [a["data"] for a in json.load(r).get("Answer", []) if a.get("type") == 15]
        if not ans:
            return None
        host = sorted(ans, key=lambda x: int(x.split()[0]))[0].split()[1].rstrip(".")
        parts = host.split(".")
        return ".".join(parts[-2:]) if len(parts) >= 2 else host
    except Exception:
        return None


def _autodiscover(email):
    domain = email.split("@")[-1].lower()
    cached = _disc_cache(domain)
    if cached:
        return cached
    result = None
    for url in (f"https://autoconfig.thunderbird.net/v1.1/{domain}",
                f"https://autoconfig.{domain}/mail/config-v1.1.xml",
                f"https://{domain}/.well-known/autoconfig/mail/config-v1.1.xml"):
        result = _fetch(url)
        if result:
            break
    if not result:
        mxd = _mx_domain(domain)
        if mxd and mxd != domain:
            result = _fetch(f"https://autoconfig.thunderbird.net/v1.1/{mxd}")
    if result:
        _disc_cache(domain, result)
    return result


# ---- output helpers ---------------------------------------------------------
def out(obj):
    print(json.dumps(obj, ensure_ascii=False, default=str))


def die(msg, code=1):
    out({"error": str(msg)})
    sys.exit(code)


def _h(raw):
    """Decode a possibly RFC2047-encoded header to a plain str."""
    if not raw:
        return ""
    try:
        return str(make_header(decode_header(raw)))
    except Exception:
        return str(raw)


# ---- IMAP -------------------------------------------------------------------
def imap_connect(cfg):
    if not (cfg["user"] and cfg["password"]):
        die("missing EMAIL_USER / EMAIL_PASS in ~/.env")
    if not cfg["imap_host"]:
        die(f"could not autodiscover IMAP settings for {cfg['user']} "
            f"(domain not in ISPDB/autoconfig and no MX match). "
            f"Set EMAIL_IMAP_HOST (+ EMAIL_IMAP_PORT / EMAIL_IMAP_SSL) in ~/.env.")
    try:
        if cfg["imap_ssl"]:
            M = imaplib.IMAP4_SSL(cfg["imap_host"], cfg["imap_port"])
        else:
            M = imaplib.IMAP4(cfg["imap_host"], cfg["imap_port"])
            if cfg["imap_starttls"]:
                M.starttls()
        M.login(cfg["user"], cfg["password"])
    except Exception as e:
        die(f"IMAP connect/login failed: {e}")
    return M


def _fetch_envelope(M, uid):
    """Header + flags for one UID, WITHOUT marking it seen (BODY.PEEK)."""
    typ, data = M.uid("fetch", uid,
                      "(FLAGS BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE MESSAGE-ID)])")
    if typ != "OK" or not data or data[0] is None:
        return None
    meta, header = b"", b""
    for part in data:
        if isinstance(part, tuple):
            meta += part[0] or b""
            header += part[1] or b""
        elif isinstance(part, (bytes, bytearray)):
            meta += part
    flags = imaplib.ParseFlags(meta)
    msg = message_from_bytes(header)
    return {
        "uid": uid.decode() if isinstance(uid, bytes) else str(uid),
        "from": _h(msg.get("From")),
        "to": _h(msg.get("To")),
        "subject": _h(msg.get("Subject")),
        "date": _h(msg.get("Date")),
        "message_id": (msg.get("Message-ID") or "").strip(),
        "seen": b"\\Seen" in flags,
    }


def _fetch_raw(M, uid, peek=True):
    item = "BODY.PEEK[]" if peek else "BODY[]"
    typ, data = M.uid("fetch", uid.encode(), f"({item})")
    if typ != "OK" or not data or data[0] is None:
        return None
    raw = b""
    for part in data:
        if isinstance(part, tuple):
            raw += part[1] or b""
    return message_from_bytes(raw)


# ---- body / attachment extraction -------------------------------------------
def _strip_html(html_text):
    import html as _htmlmod
    import re
    html_text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", html_text)
    html_text = re.sub(r"(?s)<[^>]+>", "", html_text)
    return _htmlmod.unescape(html_text).strip()


def _body_text(msg):
    """Return the message body as plain text (prefers text/plain; strips HTML)."""
    plain = html = None
    if msg.is_multipart():
        for part in msg.walk():
            if "attachment" in str(part.get("Content-Disposition") or ""):
                continue
            ctype = part.get_content_type()
            if ctype == "text/plain" and plain is None:
                plain = part
            elif ctype == "text/html" and html is None:
                html = part
    else:
        plain = msg if msg.get_content_type() != "text/html" else None
        html = msg if msg.get_content_type() == "text/html" else None
    target = plain or html
    if target is None:
        return ""
    payload = target.get_payload(decode=True) or b""
    text = payload.decode(target.get_content_charset() or "utf-8", "replace")
    if target is html:
        text = _strip_html(text)
    return text


def _attachments(msg):
    names = []
    if msg.is_multipart():
        for part in msg.walk():
            if "attachment" in str(part.get("Content-Disposition") or ""):
                names.append(_h(part.get_filename()) or "unnamed")
    return names


# ---- SMTP -------------------------------------------------------------------
# Standard special-use folders (RFC 6154) and their canonical display names.
_SPECIAL_KINDS = {"sent": "Sent", "drafts": "Drafts",
                  "trash": "Trash", "junk": "Junk"}


def _namespace(M):
    """Personal namespace (prefix, separator) from the server, e.g.
    ('INBOX.', '.') on OVH, ('', '/') on Gmail. Never guess these — a wrong
    guess is exactly what creates doubled-prefix folders like INBOX.INBOX.Sent."""
    try:
        typ, data = M.namespace()
        if typ == "OK" and data and data[0]:
            s = data[0].decode() if isinstance(data[0], (bytes, bytearray)) else str(data[0])
            m = re.search(r'\(\("([^"]*)"\s+"?([^")]*)"?\)\)', s)
            if m:
                prefix, sep = m.group(1), m.group(2)
                if sep in ("", "NIL"):
                    sep = "/"
                return prefix, sep
    except Exception:
        pass
    return "", "/"


def _list_folders(M):
    """LIST parsed into [(flags_lowercase, exact_mailbox_name)]."""
    typ, data = M.list()
    rows = []
    for line in (data or []):
        if not line:
            continue
        s = line.decode() if isinstance(line, (bytes, bytearray)) else str(line)
        m = re.match(r'\((?P<flags>[^)]*)\)\s+(?:"[^"]*"|\S+)\s+(?P<name>.+)$', s)
        if not m:
            continue
        rows.append((m.group("flags").lower(),
                     m.group("name").strip().strip('"')))
    return rows


def _resolve_special(M, kind, create=False):
    """Resolve a special-use folder in a provider-agnostic way. Precedence:
      1. SPECIAL-USE flag (\\Sent etc.) — Gmail/Fastmail advertise these
      2. the STANDARD name = <personal-namespace-prefix> + <Name> (INBOX.Sent)
      3. the SHALLOWEST folder whose leaf matches (so INBOX.Sent always wins
         over doubled-prefix debris like INBOX.INBOX.Sent)
      4. if create=True and none exist, create the standard name
    Always returns the server's exact mailbox name — never a constructed one,
    except the standard name we deliberately create."""
    prefix, sep = _namespace(M)
    name_cap = _SPECIAL_KINDS[kind]
    rows = _list_folders(M)
    names = [n for _, n in rows]
    # 1. SPECIAL-USE flag
    for flags, name in rows:
        if "\\" + kind in flags:
            return name
    # 2. standard location directly under the personal namespace
    std = prefix + name_cap
    if std in names:
        return std
    # 3. shallowest leaf-name match (avoids the doubled-prefix debris)
    cands = [n for n in names if re.split(r"[./]", n)[-1].strip().lower() == kind]
    if cands:
        return sorted(cands, key=lambda n: len(re.split(r"[./]", n)))[0]
    # 4. nothing exists — create the standard one on demand
    if create:
        try:
            M.create(_imap_folder(std))
            return std
        except Exception:
            return None
    return None


def _find_sent(M):
    return _resolve_special(M, "sent")


def _append_sent(cfg, msg):
    """Save a copy of an outgoing message to the Sent folder (SMTP doesn't).
    Creates the standard Sent folder if the mailbox has none."""
    import time
    M = imap_connect(cfg)
    try:
        sent = _resolve_special(M, "sent", create=True)
        if sent:
            M.append(_imap_folder(sent), "(\\Seen)",
                     imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    finally:
        try:
            M.logout()
        except Exception:
            pass


def _send(cfg, msg):
    if not (cfg["user"] and cfg["password"]):
        die("missing EMAIL_USER / EMAIL_PASS in ~/.env")
    if not cfg["smtp_host"]:
        die(f"could not autodiscover SMTP settings for {cfg['user']} "
            f"(domain not in ISPDB/autoconfig and no MX match). "
            f"Set EMAIL_SMTP_HOST (+ EMAIL_SMTP_PORT / EMAIL_SMTP_MODE) in ~/.env.")
    # Stamp Date + Message-ID (smtplib adds neither; without Message-ID reply
    # threading breaks and deliverability/spam scoring suffers).
    if "Date" not in msg:
        msg["Date"] = formatdate(localtime=True)
    if "Message-ID" not in msg:
        domain = (cfg["user"] or "").split("@")[-1] or None
        msg["Message-ID"] = make_msgid(domain=domain)
    try:
        if cfg["smtp_mode"] == "ssl":
            s = smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"])
        else:
            s = smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"])
            if cfg["smtp_mode"] == "starttls":
                s.starttls()
        s.login(cfg["user"], cfg["password"])
        s.send_message(msg)
        s.quit()
    except Exception as e:
        die(f"SMTP send failed: {e}")
    # save a copy to Sent so sent mail is visible (best-effort; SMTP doesn't append)
    try:
        _append_sent(cfg, msg)
    except Exception:
        pass


# ---- commands ---------------------------------------------------------------
def _imap_folder(name):
    return '"%s"' % name if " " in name else name


def cmd_folders(cfg, args):
    """List mailboxes and identify special-use ones (\\Sent, \\Drafts, \\Trash),
    resolved namespace-aware and provider-agnostic (see _resolve_special)."""
    M = imap_connect(cfg)
    try:
        prefix, sep = _namespace(M)
        names = [n for _, n in _list_folders(M)]
        special = {}
        for kind in _SPECIAL_KINDS:
            name = _resolve_special(M, kind)
            if name:
                special[kind] = name
        out({"folders": names, "special": special,
             "namespace": {"prefix": prefix, "sep": sep}})
    finally:
        try:
            M.logout()
        except Exception:
            pass


def cmd_inbox(cfg, args):
    M = imap_connect(cfg)
    try:
        folder = getattr(args, "folder", None) or cfg["mailbox"]
        styp, _ = M.select(_imap_folder(folder), readonly=True)
        if styp != "OK":
            die(f"folder not found: {folder}")
        typ, data = M.uid("search", None, "UNSEEN" if args.unread else "ALL")
        if typ != "OK":
            die(f"search failed: {typ}")
        uids = data[0].split()
        if args.limit:
            uids = uids[-args.limit:]
        uids = list(reversed(uids))  # newest first
        envs = [e for e in (_fetch_envelope(M, u) for u in uids) if e]
        out({"mailbox": cfg["mailbox"], "count": len(envs), "envelopes": envs})
    finally:
        try:
            M.logout()
        except Exception:
            pass


def cmd_read(cfg, args):
    M = imap_connect(cfg)
    try:
        folder = getattr(args, "folder", None) or cfg["mailbox"]
        styp, _ = M.select(_imap_folder(folder), readonly=not args.mark_seen)
        if styp != "OK":
            die(f"folder not found: {folder}")
        msg = _fetch_raw(M, args.uid, peek=not args.mark_seen)
        if msg is None:
            die(f"message uid {args.uid} not found")
        out({
            "uid": args.uid,
            "from": _h(msg.get("From")),
            "to": _h(msg.get("To")),
            "cc": _h(msg.get("Cc")),
            "subject": _h(msg.get("Subject")),
            "date": _h(msg.get("Date")),
            "message_id": (msg.get("Message-ID") or "").strip(),
            "attachments": _attachments(msg),
            "body": _body_text(msg),
        })
    finally:
        try:
            M.logout()
        except Exception:
            pass


def cmd_send(cfg, args):
    if not cfg["user"]:
        die("missing EMAIL_USER in ~/.env")
    msg = EmailMessage()
    msg["From"] = cfg["user"]
    msg["To"] = args.to
    if args.cc:
        msg["Cc"] = args.cc
    msg["Subject"] = args.subject
    if args.html:
        msg.set_content("This message is best viewed in an HTML-capable client.")
        msg.add_alternative(args.body, subtype="html")
    else:
        msg.set_content(args.body)
    _send(cfg, msg)
    out({"ok": True, "to": args.to, "cc": args.cc, "subject": args.subject})


def cmd_reply(cfg, args):
    M = imap_connect(cfg)
    try:
        M.select(cfg["mailbox"], readonly=True)
        orig = _fetch_raw(M, args.uid, peek=True)
        if orig is None:
            die(f"message uid {args.uid} not found")
    finally:
        try:
            M.logout()
        except Exception:
            pass

    to_addr = parseaddr(orig.get("Reply-To") or orig.get("From") or "")[1]
    if not to_addr:
        die("could not determine reply address")
    subject = _h(orig.get("Subject")) or ""
    if not subject.lower().startswith("re:"):
        subject = "Re: " + subject
    orig_id = (orig.get("Message-ID") or "").strip()
    refs = (orig.get("References") or "").strip()
    references = (refs + " " + orig_id).strip() if orig_id else refs

    msg = EmailMessage()
    msg["From"] = cfg["user"]
    msg["To"] = to_addr
    if args.all:
        extra = [a for _, a in getaddresses([orig.get("To", ""), orig.get("Cc", "")])
                 if a and a.lower() != (cfg["user"] or "").lower() and a.lower() != to_addr.lower()]
        if extra:
            msg["Cc"] = ", ".join(dict.fromkeys(extra))
    msg["Subject"] = subject
    if orig_id:
        msg["In-Reply-To"] = orig_id
    if references:
        msg["References"] = references
    msg.set_content(args.body)
    _send(cfg, msg)
    out({"ok": True, "to": to_addr, "subject": subject, "in_reply_to": orig_id})


def cmd_search(cfg, args):
    M = imap_connect(cfg)
    try:
        mbox = getattr(args, "folder", None) or cfg["mailbox"]
        styp, _ = M.select(_imap_folder(mbox), readonly=True)
        if styp != "OK":
            die(f"cannot open folder {mbox}")
        text = getattr(args, "text", None)
        if text is not None:
            # free-text search across the WHOLE message (headers + body) via IMAP
            # TEXT; quote it so multi-word phrases are one criterion. UTF-8 charset
            # so non-ASCII queries work.
            q = text.replace("\\", "\\\\").replace('"', '\\"')
            try:
                typ, data = M.uid("search", "UTF-8", "TEXT", '"%s"' % q)
            except Exception:
                typ, data = M.uid("search", None, "TEXT", '"%s"' % q)
            label = text
        else:
            typ, data = M.uid("search", None, *args.query.split())
            label = args.query
        if typ != "OK":
            die(f"search failed: {typ}")
        uids = data[0].split()
        if args.limit:
            uids = uids[-args.limit:]
        uids = list(reversed(uids))
        envs = [e for e in (_fetch_envelope(M, u) for u in uids) if e]
        out({"query": label, "count": len(envs), "envelopes": envs})
    finally:
        try:
            M.logout()
        except Exception:
            pass


def cmd_discover(cfg, args):
    email = args.email or cfg["user"]
    if not email:
        die("provide an address: email-agent discover <email> (or set EMAIL_USER)")
    disc = _autodiscover(email)
    if not disc:
        out({"email": email, "discovered": False,
             "note": "not in ISPDB/autoconfig and no MX match — set EMAIL_IMAP_HOST/EMAIL_SMTP_HOST manually"})
        return
    imap, smtp = disc
    out({"email": email, "discovered": True, "imap": imap, "smtp": smtp})


# ---- CLI --------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        prog="email-agent",
        description="Agent-native CLI email client — JSON output, stdlib, ~/.env config.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("inbox", help="list envelopes as JSON (newest first)")
    pi.add_argument("--unread", action="store_true", help="only unseen messages")
    pi.add_argument("--limit", type=int, default=20)
    pi.add_argument("--folder", default=None, help="mailbox/folder to list (default INBOX)")

    sub.add_parser("folders", help="list folders + special-use (Sent/Drafts/...)")

    pr = sub.add_parser("read", help="print one message as JSON")
    pr.add_argument("uid")
    pr.add_argument("--mark-seen", action="store_true", help="mark the message \\Seen")
    pr.add_argument("--folder", default=None, help="folder the uid lives in (default INBOX)")

    ps = sub.add_parser("send", help="send a message")
    ps.add_argument("--to", required=True)
    ps.add_argument("--subject", required=True)
    ps.add_argument("--body", required=True)
    ps.add_argument("--cc")
    ps.add_argument("--html", action="store_true", help="treat --body as HTML")

    prp = sub.add_parser("reply", help="threaded reply to a uid")
    prp.add_argument("uid")
    prp.add_argument("--body", required=True)
    prp.add_argument("--all", action="store_true", help="reply-all (Cc original recipients)")

    psr = sub.add_parser("search", help="search messages (raw IMAP criteria, or --text)")
    psr.add_argument("query", nargs="?", default="ALL", help='raw IMAP criteria, e.g. "FROM boss@x.com UNSEEN"')
    psr.add_argument("--text", help="free-text search across headers + body (from/subject/body)")
    psr.add_argument("--folder", help="folder to search (default INBOX)")
    psr.add_argument("--limit", type=int, default=20)

    pd = sub.add_parser("discover", help="show autodiscovered IMAP/SMTP settings (no login)")
    pd.add_argument("email", nargs="?", help="address to probe (defaults to EMAIL_USER)")

    args = p.parse_args()
    cfg = load_config()
    {
        "inbox": cmd_inbox,
        "folders": cmd_folders,
        "read": cmd_read,
        "send": cmd_send,
        "reply": cmd_reply,
        "search": cmd_search,
        "discover": cmd_discover,
    }[args.cmd](cfg, args)


if __name__ == "__main__":
    main()
