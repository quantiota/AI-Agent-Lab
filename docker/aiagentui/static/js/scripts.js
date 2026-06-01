document.getElementById('claude-api-form').addEventListener('submit', function(event) {
  event.preventDefault();
  const apiKey = document.getElementById('api-key-input').value.trim();
  if (apiKey) {
      alert(`API Key Submitted: ${apiKey}`);
      // Add logic to handle the Anthropic API key submission if needed
  } else {
      alert('Please enter your API key.');
  }
});

// ---- Chat history (stored in localStorage) ----
let chats = [];            // [{ id, title, messages: [{role, content, display?}] }]
let currentChatId = null;
let attachedFile = null;   // { name, content } pending attachment

function loadChats() {
  try { chats = JSON.parse(localStorage.getItem('aiagent_chats')) || []; }
  catch (e) { chats = []; }
}

function saveChats() {
  localStorage.setItem('aiagent_chats', JSON.stringify(chats));
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

// ---- File attachment (text files, read client-side) ----
function handleAttach(event) {
  const file = event.target.files[0];
  if (!file) return;
  const MAX_BYTES = 200 * 1024; // 200 KB of text
  if (file.size > MAX_BYTES) {
    alert('File is too large to attach (max 200 KB of text).');
    event.target.value = '';
    return;
  }
  const reader = new FileReader();
  reader.onload = e => { attachedFile = { name: file.name, content: e.target.result }; renderAttachment(); };
  reader.onerror = () => alert('Could not read the file.');
  reader.readAsText(file);
  event.target.value = ''; // allow re-selecting the same file
}

function renderAttachment() {
  const el = document.getElementById('chat-attachment');
  if (!el) return;
  if (!attachedFile) { el.style.display = 'none'; el.innerHTML = ''; return; }
  el.style.display = 'flex';
  const name = attachedFile.name.replace(/[<>&]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c]));
  el.innerHTML =
    `<span class="attachment-chip">📎 <span class="attachment-name">${name}</span>` +
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
  if (attachedFile) {
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

  fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    // strip the display-only field before sending to the API
    body: JSON.stringify({ messages: chat.messages.map(m => ({ role: m.role, content: m.content })), model })
  })
  .then(response => response.json())
  .then(data => {
    if (data.response) {
      chat.messages.push({ role: 'assistant', content: data.response });
      renderChat();
      saveChats();
    } else {
      appendMessage('bot', data.error || 'No response.');   // errors are shown but not stored
    }
  })
  .catch(() => appendMessage('bot', 'Error communicating with AI.'));
}

function appendMessage(sender, text) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${sender}-message`;
  messageDiv.innerHTML = `<span class="message-text">${text}</span>`;
  document.getElementById('chatbot-body').appendChild(messageDiv);
  document.getElementById('chatbot-body').scrollTop = document.getElementById('chatbot-body').scrollHeight;
}

// Initialise chat history on load
document.addEventListener('DOMContentLoaded', function () {
  loadChats();
  renderHistory();
  renderChat();
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
  return { light: `/static/img/${base}-black.svg`, dark: `/static/img/${base}-white.svg` };
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
  fetch('/upload', { method: 'POST', body: fd })
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
  const isDark = document.body.classList.contains('is-dark');
  files.slice().sort((a, b) => a.localeCompare(b)).forEach(name => {
    const icon = uploadFileIcon(name);
    const row = document.createElement('div');
    row.className = 'upload-file-row';
    row.innerHTML =
      `<img class="ufr-icon" alt="" src="${isDark ? icon.dark : icon.light}" data-icon-light="${icon.light}" data-icon-dark="${icon.dark}" />` +
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
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
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
  fetch('/restart/nginx')
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
  fetch('/restart/' + container).catch(console.error);
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
      headers: { 'Content-Type': 'application/json' },
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