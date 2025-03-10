// API endpoint URL
const apiUrl = 'http://127.0.0.1:5000';
let currentKey = '';

// Function to fetch generated key from the backend
document.getElementById('generate-key').addEventListener('click', () => {
    fetch(`${apiUrl}/generate_key`)
        .then(response => response.json())
        .then(data => {
            if (data.key) {
                currentKey = data.key;
                document.getElementById('key').value = data.key;
                document.getElementById('result-output').textContent = 'New key generated successfully!';
            }
        })
        .catch(error => {
            document.getElementById('result-output').textContent = 'Error generating key: ' + error;
        });
});

// Function to encrypt the message
document.getElementById('encrypt-btn').addEventListener('click', () => {
    const message = document.getElementById('message').value;
    const key = document.getElementById('key').value;

    if (!message) {
        document.getElementById('result-output').textContent = 'Please enter a message to encrypt!';
        return;
    }
    
    if (!key) {
        document.getElementById('result-output').textContent = 'Please generate a key first!';
        return;
    }

    fetch(`${apiUrl}/encrypt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, key: key })
    })
    .then(response => response.json())
    .then(data => {
        if (data.encrypted_message) {
            document.getElementById('encrypted-message').value = data.encrypted_message;
            document.getElementById('result-output').textContent = 'Message encrypted successfully!';
        } else {
            document.getElementById('result-output').textContent = 'Error: ' + data.error;
        }
    })
    .catch(error => {
        document.getElementById('result-output').textContent = 'Error encrypting message: ' + error;
    });
});

// Function to decrypt the message
document.getElementById('decrypt-btn').addEventListener('click', () => {
    const encryptedMessage = document.getElementById('encrypted-message').value;
    const key = document.getElementById('key').value;

    if (!encryptedMessage) {
        document.getElementById('result-output').textContent = 'Please enter an encrypted message!';
        return;
    }
    
    if (!key) {
        document.getElementById('result-output').textContent = 'Please generate a key first!';
        return;
    }

    fetch(`${apiUrl}/decrypt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ encrypted_message: encryptedMessage, key: key })
    })
    .then(response => response.json())
    .then(data => {
        if (data.decrypted_message) {
            document.getElementById('result-output').textContent = 'Decrypted Message:\n' + data.decrypted_message;
        } else {
            document.getElementById('result-output').textContent = 'Error: ' + data.error;
        }
    })
    .catch(error => {
        document.getElementById('result-output').textContent = 'Error decrypting message: ' + error;
    });
});