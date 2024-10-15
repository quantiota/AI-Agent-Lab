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
