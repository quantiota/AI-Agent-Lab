// CSRF token — read fresh from the <meta name="csrf-token"> tag (set in index.html) on each call.
function getCsrf() {
  const m = document.querySelector('meta[name="csrf-token"]');
  return m ? m.content : '';
}

document.getElementById('claude-api-form').addEventListener('submit', function(event) {
  event.preventDefault();
  const input = document.getElementById('api-key-input');
  const apiKey = input.value.trim();
  if (!apiKey) {
    alert('Please enter your API key.');
    return;
  }
  fetch('/save-key', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
    body: JSON.stringify({ apiKey: apiKey })
  })
    .then(r => r.json().then(d => ({ ok: r.ok, d })))
    .then(({ ok, d }) => {
      alert(d.message || (ok ? 'API key saved.' : 'Could not save key.'));
      if (ok) {
        input.value = '';
        closeModal('claude');
      }
    })
    .catch(() => alert('Could not save the key. Please try again.'));
});

document.getElementById('jupyterhub-api-form').addEventListener('submit', function(event) {
  event.preventDefault();
  const url   = document.getElementById('jh-url-input').value.trim();
  const user  = document.getElementById('jh-user-input').value.trim();
  const token = document.getElementById('jh-token-input').value.trim();
  if (!url || !user || !token) {
    alert('Please enter the Hub URL, username, and token.');
    return;
  }
  fetch('/save-jh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
    body: JSON.stringify({ url: url, user: user, token: token })
  })
    .then(r => r.json().then(d => ({ ok: r.ok, d })))
    .then(({ ok, d }) => {
      alert(d.message || (ok ? 'JupyterHub connection saved.' : 'Could not save.'));
      if (ok) {
        document.getElementById('jh-token-input').value = '';
        closeModal('jupyterhub');
      }
    })
    .catch(() => alert('Could not save. Please try again.'));
});

// ---- Chat history (persisted server-side via /chats — survives browser wipe + follows the user across devices) ----
let chats = [];            // [{ id, title, messages: [{role, content, display?}] }]
let currentChatId = null;
let attachedFile = null;   // { name, content } pending attachment

// Returns a promise — startup must await it before rendering.
function loadChats() {
  return fetch('/chats')
    .then(r => (r.ok ? r.json() : []))
    .then(data => { chats = Array.isArray(data) ? data : []; })
    .catch(() => { chats = []; });
}

function saveChats() {
  fetch('/chats', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
    body: JSON.stringify(chats)
  }).catch(() => {});
}

function currentChat() {
  return chats.find(c => c.id === currentChatId) || null;
}

function ensureChat() {
  let chat = currentChat();
  if (!chat) {
    chat = { id: Date.now().toString(), title: 'New chat', messages: [] };
    chats.unshift(chat);
    currentChatId = chat.id;
  }
  return chat;
}

function newChat() {
  currentChatId = null;   // a fresh chat is created on the first message
  renderChat();
  renderHistory();
  const input = document.getElementById('chatbot-input');
  if (input) input.focus();
}

function loadChat(id) {
  currentChatId = id;
  renderChat();
  renderHistory();
}

// ---- Search chats ----
function openSearch() {
  openModal('search');
  const input = document.getElementById('search-input');
  if (input) input.value = '';
  searchChats();
  setTimeout(() => input && input.focus(), 50);
}

function searchChats() {
  const results = document.getElementById('search-results');
  if (!results) return;
  const q = (document.getElementById('search-input').value || '').trim().toLowerCase();

  let matches;
  if (!q) {
    matches = chats.map(c => ({ chat: c, snippet: '' }));
  } else {
    matches = [];
    chats.forEach(c => {
      let hit = (c.title || '').toLowerCase().includes(q);
      let snippet = '';
      for (const m of c.messages) {
        const text = m.display || m.content || '';
        const idx = text.toLowerCase().indexOf(q);
        if (idx !== -1) {
          hit = true;
          const start = Math.max(0, idx - 30);
          snippet = (start > 0 ? '…' : '') + text.slice(start, idx + q.length + 40).replace(/\s+/g, ' ').trim() + '…';
          break;
        }
      }
      if (hit) matches.push({ chat: c, snippet });
    });
  }

  if (matches.length === 0) {
    results.innerHTML = '<div class="search-empty">No matching chats.</div>';
    return;
  }

  const esc = s => (s || '').replace(/[<>&]/g, ch => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[ch]));
  results.innerHTML = matches.map(({ chat, snippet }) =>
    `<div class="search-result" onclick="openSearchResult('${chat.id}')">` +
      `<div class="search-result-title">${esc(chat.title || 'New chat')}</div>` +
      (snippet ? `<div class="search-result-snippet">${esc(snippet)}</div>` : '') +
    `</div>`
  ).join('');
}

function openSearchResult(id) {
  closeModal('search');
  loadChat(id);
}

function renderChat() {
  const body = document.getElementById('chatbot-body');
  const chat = currentChat();
  if (!chat || chat.messages.length === 0) {
    body.innerHTML = '<div class="chat-greeting"><h2>What can I help with?</h2></div>';
    return;
  }
  body.innerHTML = '';
  chat.messages.forEach(m => appendMessage(m.role === 'assistant' ? 'bot' : 'user', m.display || m.content));
}

// ---- File attachment (text read as text; images read as base64 for vision) ----
const IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];

function handleAttach(event) {
  const file = event.target.files[0];
  if (file) attachFile(file);
  event.target.value = ''; // allow re-selecting the same file
}

function attachFile(file) {
  // Images → base64 data URL (sent as a vision block); everything else → text.
  if (IMAGE_TYPES.includes(file.type)) {
    const MAX_BYTES = 2 * 1024 * 1024; // 2 MB — kept modest (re-sent each turn + stored)
    if (file.size > MAX_BYTES) { alert('Image is too large to attach (max 2 MB).'); return; }
    const reader = new FileReader();
    reader.onload = e => {
      const dataUrl = e.target.result;               // data:image/png;base64,XXXX
      attachedFile = {
        name: file.name || 'image', kind: 'image', mediaType: file.type,
        data: (dataUrl.split(',')[1] || ''), dataUrl
      };
      renderAttachment();
    };
    reader.onerror = () => alert('Could not read the image.');
    reader.readAsDataURL(file);
    return;
  }
  // PDFs → base64 document block (Claude reads text + figures natively).
  if (file.type === 'application/pdf') {
    const MAX_BYTES = 10 * 1024 * 1024; // 10 MB — re-sent each turn, so kept bounded
    if (file.size > MAX_BYTES) { alert('PDF is too large to attach (max 10 MB).'); return; }
    const reader = new FileReader();
    reader.onload = e => {
      attachedFile = {
        name: file.name || 'document.pdf', kind: 'pdf',
        mediaType: 'application/pdf', data: (e.target.result.split(',')[1] || '')
      };
      renderAttachment();
    };
    reader.onerror = () => alert('Could not read the PDF.');
    reader.readAsDataURL(file);
    return;
  }
  const MAX_BYTES = 200 * 1024; // 200 KB of text
  if (file.size > MAX_BYTES) { alert('File is too large to attach (max 200 KB of text).'); return; }
  const reader = new FileReader();
  reader.onload = e => { attachedFile = { name: file.name, kind: 'text', content: e.target.result }; renderAttachment(); };
  reader.onerror = () => alert('Could not read the file.');
  reader.readAsText(file);
}

function renderAttachment() {
  const el = document.getElementById('chat-attachment');
  if (!el) return;
  if (!attachedFile) { el.style.display = 'none'; el.innerHTML = ''; return; }
  el.style.display = 'flex';
  const name = attachedFile.name.replace(/[<>&]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c]));
  const lead = attachedFile.kind === 'image'
    ? `<img src="${attachedFile.dataUrl}" alt="" class="attachment-thumb" />`
    : (attachedFile.kind === 'pdf' ? '📄 ' : '📎 ');
  el.innerHTML =
    `<span class="attachment-chip">${lead}<span class="attachment-name">${name}</span>` +
    `<button type="button" class="attachment-remove" onclick="clearAttachment()" title="Remove">✕</button></span>`;
}

function clearAttachment() {
  attachedFile = null;
  renderAttachment();
}

function renderHistory() {
  const section = document.getElementById('chat-history');
  if (!section) return;
  if (chats.length === 0) { section.innerHTML = ''; return; }
  let html = '<span class="history-label">Recents</span>';
  chats.forEach(c => {
    const active = c.id === currentChatId ? ' active' : '';
    const title = (c.title || 'New chat').replace(/[<>&]/g, ch => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[ch]));
    html +=
      `<div class="history-item${active}" onclick="loadChat('${c.id}')" title="${title}">` +
        `<span class="history-item-title">${title}</span>` +
        `<button class="history-item-delete" type="button" title="Delete conversation" aria-label="Delete conversation" onclick="event.stopPropagation(); deleteChat('${c.id}')">` +
          `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>` +
        `</button>` +
      `</div>`;
  });
  section.innerHTML = html;
}

function deleteChat(id) {
  const chat = chats.find(c => c.id === id);
  if (!chat) return;
  if (!confirm(`Delete "${chat.title || 'New chat'}"? This cannot be undone.`)) return;
  chats = chats.filter(c => c.id !== id);
  if (currentChatId === id) {   // deleted the open chat → fall back to the greeting
    currentChatId = null;
    renderChat();
  }
  saveChats();
  renderHistory();
}

function sendMessage() {
  const input = document.getElementById('chatbot-input');
  const typed = input.value.trim();
  if (!typed && !attachedFile) return;

  const model = document.getElementById('model-select')?.value;

  // What the model receives (includes the file) vs what the UI shows (clean)
  let apiContent = typed;
  let displayContent = typed;
  if (attachedFile && attachedFile.kind === 'image') {
    // Vision: an image block + a text block; the UI shows the image inline.
    apiContent = [
      { type: 'image', source: { type: 'base64', media_type: attachedFile.mediaType, data: attachedFile.data } },
      { type: 'text', text: typed || 'Describe and explain this image.' }
    ];
    displayContent = (typed ? typed + '\n\n' : '') + `<img src="${attachedFile.dataUrl}" alt="${attachedFile.name}" class="chat-image" />`;
  } else if (attachedFile && attachedFile.kind === 'pdf') {
    // Document Q&A: a PDF document block + a text block; UI shows a filename chip.
    apiContent = [
      { type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: attachedFile.data } },
      { type: 'text', text: typed || 'Summarize this document and list its key points.' }
    ];
    displayContent = (typed ? typed + '\n\n' : '') + `📄 ${attachedFile.name}`;
  } else if (attachedFile) {
    apiContent = `Attached file "${attachedFile.name}":\n\n${attachedFile.content}` + (typed ? `\n\n${typed}` : '');
    displayContent = (typed ? typed + '\n\n' : '') + `📎 ${attachedFile.name}`;
  }

  const chat = ensureChat();
  chat.messages.push({ role: 'user', content: apiContent, display: displayContent });
  if (!chat.title || chat.title === 'New chat') {
    chat.title = (typed || attachedFile.name).slice(0, 40);
  }
  input.value = '';
  clearAttachment();
  renderChat();
  renderHistory();
  saveChats();

  // Stream the reply into a bot bubble, re-rendering markdown as chunks arrive.
  const botEl = appendMessage('bot', '');
  const textSpan = botEl.querySelector('.message-text');
  const body = document.getElementById('chatbot-body');
  let full = '';

  fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
    // strip the display-only field before sending to the API
    body: JSON.stringify({ messages: chat.messages.map(m => ({ role: m.role, content: m.content })), model })
  })
  .then(async response => {
    if (!response.ok || !response.body) {
      const err = await response.text().catch(() => '');
      botEl._rawText = err || 'Error communicating with AI.';
      textSpan.innerHTML = renderMarkdown(botEl._rawText);
      return;
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      full += decoder.decode(value, { stream: true });
      textSpan.innerHTML = renderMarkdown(full);
      botEl._rawText = full;
      body.scrollTop = body.scrollHeight;
    }
    if (full.trim()) {
      chat.messages.push({ role: 'assistant', content: full });
      saveChats();
    }
  })
  .catch(() => { textSpan.innerHTML = renderMarkdown('Error communicating with AI.'); });
}

// Enable LaTeX math ($…$ inline, $$…$$ display). output:'html' keeps KaTeX from
// emitting MathML — that's what crashed Chrome on the blog.
if (window.marked && window.markedKatex) {
  marked.use(markedKatex({ throwOnError: false, output: 'html' }));
}

function renderMarkdown(text) {
  try { return (window.marked ? marked.parse(text) : text); }
  catch (e) { return text; }
}

const COPY_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
const CHECK_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';

// Copy the bot reply's raw markdown source (not the rendered HTML).
function copyMessage(el, btn) {
  navigator.clipboard.writeText(el._rawText || '').then(() => {
    btn.innerHTML = CHECK_SVG;
    btn.classList.add('copied');
    setTimeout(() => { btn.innerHTML = COPY_SVG; btn.classList.remove('copied'); }, 1200);
  }).catch(() => {});
}

function appendMessage(sender, text) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${sender}-message`;
  const html = sender === 'bot' ? renderMarkdown(text) : text;
  messageDiv.innerHTML = `<span class="message-text">${html}</span>`;
  if (sender === 'bot') {
    messageDiv._rawText = text;   // kept in sync as the stream fills in
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'message-copy';
    btn.title = 'Copy';
    btn.setAttribute('aria-label', 'Copy message');
    btn.innerHTML = COPY_SVG;
    btn.onclick = () => copyMessage(messageDiv, btn);
    messageDiv.appendChild(btn);
  }
  const body = document.getElementById('chatbot-body');
  body.appendChild(messageDiv);
  body.scrollTop = body.scrollHeight;
  return messageDiv;
}

// Initialise chat history on load
document.addEventListener('DOMContentLoaded', function () {
  loadChats().then(() => {
    renderHistory();
    renderChat();
  });
});

// Prefill the chat input with a starter prompt (used by the suggestion chips)
function usePrompt(text) {
  const input = document.getElementById('chatbot-input');
  input.value = text;
  input.focus();
}

// --- Custom model dropdown ---
function toggleModelMenu(event) {
  event.stopPropagation();
  const menu = document.getElementById('model-menu');
  const willOpen = menu.hidden;
  menu.hidden = !willOpen;
  document.getElementById('model-dropdown').classList.toggle('open', willOpen);
  document.getElementById('model-selector-btn').setAttribute('aria-expanded', willOpen ? 'true' : 'false');
}

function selectModel(option) {
  document.getElementById('model-select').value = option.dataset.model;
  document.getElementById('model-label').textContent = option.textContent;
  document.querySelectorAll('#model-menu .model-option').forEach(o =>
    o.setAttribute('aria-selected', o === option ? 'true' : 'false'));
  closeModelMenu();
}

function closeModelMenu() {
  const menu = document.getElementById('model-menu');
  if (menu) menu.hidden = true;
  const dropdown = document.getElementById('model-dropdown');
  if (dropdown) dropdown.classList.remove('open');
  const btn = document.getElementById('model-selector-btn');
  if (btn) btn.setAttribute('aria-expanded', 'false');
}

// Close the model menu when clicking outside of it
document.addEventListener('click', function (e) {
  const dropdown = document.getElementById('model-dropdown');
  if (dropdown && !dropdown.contains(e.target)) closeModelMenu();
});

/* ========================
   SIDEBAR POPOVERS (per-icon dropdown)
   ======================== */
function closeSidebarPopovers() {
  document.querySelectorAll('.sidebar-popover').forEach(p => { p.hidden = true; });
  document.querySelectorAll('.sidebar-item[aria-haspopup="menu"]').forEach(b =>
    b.setAttribute('aria-expanded', 'false'));
}

function toggleSidebarPopover(event, key) {
  event.stopPropagation();
  const pop = document.getElementById('pop-' + key);
  const btn = event.currentTarget;
  if (!pop) return;

  const isOpen = !pop.hidden;
  closeSidebarPopovers();
  if (isOpen) return;            // second click closes it

  // Position as a fixed flyout to the right of the sidebar, top-aligned with the icon.
  const sidebar = document.querySelector('.icon-sidebar');
  const sb = sidebar.getBoundingClientRect();
  const r = btn.getBoundingClientRect();

  pop.hidden = false;            // unhide first so we can measure its height
  const gap = 8;
  let top = r.top;
  const maxTop = window.innerHeight - pop.offsetHeight - 8;
  if (top > maxTop) top = Math.max(8, maxTop);
  pop.style.left = (sb.right + gap) + 'px';
  pop.style.top = top + 'px';
  btn.setAttribute('aria-expanded', 'true');
}

// Close popovers on outside click, Escape, or when the layout shifts.
document.addEventListener('click', function (e) {
  if (!e.target.closest('.sidebar-item-wrap')) closeSidebarPopovers();
});
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') closeSidebarPopovers();
});
window.addEventListener('resize', closeSidebarPopovers);
document.querySelector('.icon-sidebar')?.addEventListener('scroll', closeSidebarPopovers);

function displayError(message) {
  const el = document.getElementById('error-message');
  if (!el) return;
  el.textContent = message;
  el.style.display = 'block';
}

function hideError() {
  const el = document.getElementById('error-message');
  if (el) el.style.display = 'none';
}

const UPLOAD_ALLOWED = ['.csv', '.txt', '.sql', '.pdf'];
const UPLOAD_MAX_BYTES = 800 * 1024;   // mockup: "Max size of 800K"

function uploadFileIcon(name) {
  const ext = name.slice(name.lastIndexOf('.') + 1).toLowerCase();
  const base = ({ csv: 'csv-01-stroke-rounded', txt: 'txt-01-stroke-rounded',
                  sql: 'sql-stroke-rounded',   pdf: 'pdf-01-stroke-rounded' })[ext]
                || 'txt-01-stroke-rounded';
  return `/static/img/${base}-black.svg`;   // single file; .app-icon colors it via CSS mask
}

function uploadFile(file) {
  const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
  if (!UPLOAD_ALLOWED.includes(ext)) {
    displayError(`Invalid file type: ${ext}. Allowed: CSV, TXT, SQL, PDF.`);
    return;
  }
  if (file.size > UPLOAD_MAX_BYTES) {
    displayError(`"${file.name}" is too large. Max size of 800K.`);
    return;
  }
  hideError();
  const fd = new FormData();
  fd.append('file', file);
  fetch('/upload', { method: 'POST', headers: { 'X-CSRFToken': getCsrf() }, body: fd })
    .then(r => { if (!r.ok) throw new Error('upload failed'); return r; })
    .then(() => fetchFiles())
    .catch(() => displayError('Upload failed. Please try again.'));
}

function fetchFiles() {
  fetch('/list-files')
    .then(response => response.json())
    .then(data => renderFileList(data.files || []))
    .catch(console.error);
}

function renderFileList(files) {
  const list = document.getElementById('file-list');
  if (!list) return;
  list.innerHTML = '';
  files.slice().sort((a, b) => a.localeCompare(b)).forEach(name => {
    const icon = uploadFileIcon(name);
    const row = document.createElement('div');
    row.className = 'upload-file-row';
    row.innerHTML =
      `<span class="ufr-icon app-icon" aria-hidden="true" style="--icon: url('${icon}')"></span>` +
      `<span class="ufr-name"></span>` +
      `<button class="ufr-remove" type="button" title="Remove" aria-label="Remove">` +
        `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>` +
      `</button>`;
    row.querySelector('.ufr-name').textContent = name;   // textContent: safe against odd filenames
    row.querySelector('.ufr-remove').addEventListener('click', () => deleteFile(name));
    list.appendChild(row);
  });
}

function deleteFile(filename) {
  fetch('/delete-file', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCsrf() },
    body: new URLSearchParams({ filename })
  })
    .then(response => response.json())
    .then(() => fetchFiles())
    .catch(console.error);
}

function initUpload() {
  const dz = document.getElementById('upload-dropzone');
  const input = document.getElementById('file');
  if (!dz || !input) return;
  input.addEventListener('change', () => {
    Array.from(input.files).forEach(uploadFile);
    input.value = '';
  });
  ['dragenter', 'dragover'].forEach(ev =>
    dz.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); dz.classList.add('dragover'); }));
  ['dragleave', 'dragend', 'drop'].forEach(ev =>
    dz.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); dz.classList.remove('dragover'); }));
  dz.addEventListener('drop', e => {
    if (e.dataTransfer && e.dataTransfer.files) Array.from(e.dataTransfer.files).forEach(uploadFile);
  });
  fetchFiles();
}
document.addEventListener('DOMContentLoaded', initUpload);

function restartNginx() {
  document.getElementById('nginx-message').style.display = 'block';
  fetch('/restart/nginx', { method: 'POST', headers: { 'X-CSRFToken': getCsrf() } })
    .then(() => console.log('Nginx restart initiated'))
    .catch(console.error);
}

// Restart a Docker service inline, showing the message in the same spot as nginx
function restartService(container, label) {
  const msg = document.getElementById('nginx-message');
  if (msg) {
    msg.textContent = `${label} is restarting. Please wait... then reload the page.`;
    msg.style.display = 'block';
  }
  fetch('/restart/' + container, { method: 'POST', headers: { 'X-CSRFToken': getCsrf() } }).catch(console.error);
}

function fetchBackups() {
  fetch('/api/list-backups')
    .then(response => response.json())
    .then(data => populateBackupList(data.backups))
    .catch(error => {
      console.error('Error fetching backups:', error);
      document.getElementById('status-message').textContent = 'Failed to load backups.';
    });
}

function populateBackupList(backups) {
  const menu = document.getElementById('restore-menu');
  if (!menu) return;
  menu.innerHTML = '';

  // First entry clears the selection (the "-- None --" row in the mockup)
  menu.appendChild(makeBackupOption('', '-- None --', 'Select a Backup'));

  (backups || []).forEach(({ type, timestamp }) => {
    const label = `${type} - ${timestamp}`;
    menu.appendChild(makeBackupOption(timestamp, label, label));
  });
}

// Build one <li> option; `display` is what the selector button shows when picked.
function makeBackupOption(value, text, display) {
  const li = document.createElement('li');
  li.className = 'restore-option';
  li.setAttribute('role', 'option');
  li.dataset.value = value;
  li.textContent = text;
  li.addEventListener('click', () => selectBackup(value, display));
  return li;
}

// --- Custom restore dropdown (mirrors the model dropdown) ---
function toggleRestoreMenu(event) {
  event.stopPropagation();
  const menu = document.getElementById('restore-menu');
  const willOpen = menu.hidden;
  menu.hidden = !willOpen;
  document.getElementById('restore-dropdown').classList.toggle('open', willOpen);
  document.getElementById('restore-selector-btn').setAttribute('aria-expanded', willOpen ? 'true' : 'false');
}

function closeRestoreMenu() {
  const menu = document.getElementById('restore-menu');
  if (menu) menu.hidden = true;
  const dropdown = document.getElementById('restore-dropdown');
  if (dropdown) dropdown.classList.remove('open');
  const btn = document.getElementById('restore-selector-btn');
  if (btn) btn.setAttribute('aria-expanded', 'false');
}

function selectBackup(value, display) {
  document.getElementById('restore-select').value = value;
  const label = document.getElementById('restore-label');
  label.textContent = display;
  label.classList.toggle('restore-placeholder', !value);
  document.querySelectorAll('#restore-menu .restore-option').forEach(o =>
    o.classList.toggle('active', o.dataset.value === value));
  closeRestoreMenu();
}

// Close the restore menu when clicking outside of it
document.addEventListener('click', function (e) {
  const dropdown = document.getElementById('restore-dropdown');
  if (dropdown && !dropdown.contains(e.target)) closeRestoreMenu();
});
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') closeRestoreMenu();
});

function handleRestore() {
  const selectedBackup = document.getElementById('restore-select').value;
  if (!selectedBackup) {
    document.getElementById('status-message').textContent = 'Please select a backup to restore.';
    return;
  }

  document.getElementById('restore-btn').disabled = true;
  document.getElementById('status-message').textContent = 'Restoring backup...';

  fetch('/api/restore-backup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
      body: JSON.stringify({ selectedBackup })
  })
  .then(response => response.json())
  .then(data => document.getElementById('status-message').textContent = data.message)
  .catch(error => {
      console.error('Error restoring backup:', error);
      document.getElementById('status-message').textContent = 'Failed to restore backup.';
  })
  .finally(() => document.getElementById('restore-btn').disabled = false);
}

document.addEventListener('DOMContentLoaded', function() {
  fetchFiles();
  fetchBackups();
  document.getElementById('restore-btn').addEventListener('click', handleRestore);
});