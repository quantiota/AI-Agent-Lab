// script.js
document.getElementById('openai-api-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const apiKey = document.getElementById('api-key-input').value;
    if (apiKey.trim() !== '') {
        alert('API Key Submitted: ' + apiKey);
        // TODO: Add logic to handle the OpenAI API key submission
    } else {
        alert('Please enter your API key.');
    }
});

function sendMessage() {
    const message = document.getElementById('chatbot-input').value;
    if (message.trim() !== '') {
        appendMessage('user', message);
        document.getElementById('chatbot-input').value = '';

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        }).then(response => response.json())
          .then(data => {
              if (data.error) {
                  appendMessage('bot', 'Error: ' + data.error);
              } else {
                  appendMessage('bot', data.response);
              }
          }).catch(error => {
              appendMessage('bot', 'Error communicating with AI.');
          });
    }
}

function appendMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', `${sender}-message`);
    const messageText = document.createElement('span');
    messageText.classList.add('message-text');
    messageText.textContent = text;
    messageDiv.appendChild(messageText);
    document.getElementById('chatbot-body').appendChild(messageDiv);
    document.getElementById('chatbot-body').scrollTop = document.getElementById('chatbot-body').scrollHeight;
}


function validateFile(event) {
    // Prevent form submission by default
    event.preventDefault();

    // Get the uploaded file input and its value
    const fileInput = document.getElementById('file');
    const filePath = fileInput.value;

    // Allowed file extensions
    const allowedExtensions = ['.csv', '.sql', '.pdf', '.txt'];

    // Check if a file was selected
    if (!filePath) {
        const errorMsg = 'Please select a file before uploading.';
        document.getElementById('error-message').innerText = errorMsg;
        document.getElementById('error-message').style.display = 'block';
        return; // Stop further execution
    }

    // Extract the file extension and convert to lowercase
    const fileExtension = filePath.substring(filePath.lastIndexOf('.')).toLowerCase();

    // Validate file extension
    if (!allowedExtensions.includes(fileExtension)) {
        const errorMsg = `Invalid file extension: ${fileExtension}. Allowed extensions are ${allowedExtensions.join(', ')}.`;
        document.getElementById('error-message').innerText = errorMsg;
        document.getElementById('error-message').style.display = 'block';
    } else {
        // Hide error message if the file is valid and submit the form
        document.getElementById('error-message').style.display = 'none';
        document.getElementById('upload-form').submit();  // Submit the form if validation passed
    }
}


// File Size Limit

document.querySelector('input[type="file"]').addEventListener('change', function() {
    var fileSize = this.files[0].size / 1024 / 1024; // in MB
    if (fileSize > 50) { // 50MB limit
        alert('File size exceeds 100 MB');
        this.value = ''; // Reset the input
    }
});



// Nginx  restart

function restartNginx() {
    // Show a message to the user
    document.getElementById('nginx-message').style.display = 'block';
  
    // Send an AJAX request to restart Nginx
    fetch('/restart/nginx')
      .then(response => response.text())
      .then(data => {
        console.log('Nginx restart initiated');
        // Optionally, you could add more logic here if needed
      })
      .catch(error => {
        console.error('Error restarting Nginx:', error);
      });
  }