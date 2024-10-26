document.getElementById('openai-api-form').addEventListener('submit', function(event) {
  event.preventDefault();
  const apiKey = document.getElementById('api-key-input').value.trim();
  if (apiKey) {
      alert(`API Key Submitted: ${apiKey}`);
      // Add logic to handle the OpenAI API key submission if needed
  } else {
      alert('Please enter your API key.');
  }
});

function sendMessage() {
  const message = document.getElementById('chatbot-input').value.trim();
  if (message) {
      appendMessage('user', message);
      document.getElementById('chatbot-input').value = '';

      fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message })
      })
      .then(response => response.json())
      .then(data => appendMessage('bot', data.error || data.response))
      .catch(() => appendMessage('bot', 'Error communicating with AI.'));
  }
}

function appendMessage(sender, text) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${sender}-message`;
  messageDiv.innerHTML = `<span class="message-text">${text}</span>`;
  document.getElementById('chatbot-body').appendChild(messageDiv);
  document.getElementById('chatbot-body').scrollTop = document.getElementById('chatbot-body').scrollHeight;
}

function validateFile(event) {
  event.preventDefault();
  const fileInput = document.getElementById('file');
  const filePath = fileInput.value;
  const allowedExtensions = ['.csv', '.sql', '.pdf', '.txt'];
  const fileExtension = filePath.slice(filePath.lastIndexOf('.')).toLowerCase();

  if (!filePath) {
      displayError('Please select a file before uploading.');
  } else if (!allowedExtensions.includes(fileExtension)) {
      displayError(`Invalid file extension: ${fileExtension}. Allowed extensions: ${allowedExtensions.join(', ')}.`);
  } else {
      document.getElementById('error-message').style.display = 'none';
      document.getElementById('upload-form').submit();
  }
}

function displayError(message) {
  const errorMsgElement = document.getElementById('error-message');
  errorMsgElement.textContent = message;
  errorMsgElement.style.display = 'block';
}

document.querySelector('input[type="file"]').addEventListener('change', function() {
  if (this.files[0].size / 1024 / 1024 > 50) {
      alert('File size exceeds 50 MB');
      this.value = '';
  }
});

function fetchFiles() {
  fetch('/list-files')
    .then(response => response.json())
    .then(data => renderFileList(data.files))
    .catch(console.error);
}

function renderFileList(files) {
  const fileList = document.getElementById('file-list');
  fileList.innerHTML = '';
  files.sort(compareFiles).forEach(file => {
      const fileElement = document.createElement('div');
      fileElement.className = 'file-item';
      fileElement.innerHTML = `<span>${file}</span><button onclick="deleteFile('${file}')">Delete</button>`;
      fileList.appendChild(fileElement);
  });
}

function compareFiles(a, b) {
  const [aType, aIndex] = a.split('.');
  const [bType, bIndex] = b.split('.');
  const typesOrder = { hourly: 1, daily: 2, weekly: 3, monthly: 4 };
  return (typesOrder[aType] - typesOrder[bType]) || (parseInt(aIndex) - parseInt(bIndex));
}

function deleteFile(filename) {
  fetch('/delete-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ filename })
  })
  .then(response => response.json())
  .then(result => {
      alert(result.success || result.error);
      fetchFiles();
  })
  .catch(console.error);
}

function restartNginx() {
  document.getElementById('nginx-message').style.display = 'block';
  fetch('/restart/nginx')
    .then(() => console.log('Nginx restart initiated'))
    .catch(console.error);
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
  const selectElement = document.getElementById('restore-select');
  selectElement.innerHTML = '<option value="">Select a backup</option>';
  backups.forEach(({ type, timestamp }) => {
    const option = document.createElement('option');
    option.text = `${type} - ${timestamp}`;
    option.value = timestamp;
    selectElement.add(option);
  });
}

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
