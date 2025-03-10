// API endpoint URL
const apiUrl = 'http://127.0.0.1:5000';
let currentKey = '';

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Generate initial key
    generateNewKey();
    
    // Set up event listeners
    document.getElementById('generate-key-btn').addEventListener('click', generateNewKey);
    document.getElementById('show-key-btn').addEventListener('click', toggleKeyVisibility);
    document.getElementById('generate-new-key').addEventListener('click', generateNewKey);
    document.getElementById('encrypt-message-btn').addEventListener('click', createSecureMessage);
    document.getElementById('copy-link-btn').addEventListener('click', copyShareLink);
    document.getElementById('decrypt-btn').addEventListener('click', decryptMessage);
    
    // Set up conversation list item click handlers
    setupConversationListeners();
    
    // Check if we're viewing a shared message
    checkForSharedMessage();
});

// Set up click listeners for all conversation items
function setupConversationListeners() {
    // Get all conversation items
    const conversations = document.querySelectorAll('.friend-drawer--onhover');
    
    // Add click handlers to each
    conversations.forEach(convo => {
        convo.addEventListener('click', function() {
            const messageId = this.getAttribute('data-message-id');
            
            // If it's the "New Secure Message" button
            if (this.getAttribute('data-conversation') === 'new') {
                showNewMessageForm();
            } 
            // If it's an existing message
            else if (messageId) {
                // Highlight the selected conversation
                document.querySelectorAll('.friend-drawer--onhover').forEach(c => 
                    c.classList.remove('active'));
                this.classList.add('active');
                
                // Load the message
                loadSharedMessage(messageId);
            }
        });
    });
}

// Function to show the new message form
function showNewMessageForm() {
    // Hide message results and view panels
    const messageResult = document.getElementById('message-result');
    const viewMessagePanel = document.getElementById('view-message-panel');
    const createMessagePanel = document.getElementById('create-message-panel');
    
    if (messageResult) messageResult.style.display = 'none';
    if (viewMessagePanel) viewMessagePanel.style.display = 'none';
    if (createMessagePanel) createMessagePanel.style.display = 'block';
    
    // Clear previous inputs
    const messageInput = document.getElementById('message-input');
    if (messageInput) messageInput.value = '';
    
    // Update title
    const chatTitle = document.getElementById('current-chat-title');
    if (chatTitle) chatTitle.textContent = 'New Secure Message';
}

// Function to generate a new encryption key
function generateNewKey() {
    fetch(`${apiUrl}/generate_key`)
        .then(response => response.json())
        .then(data => {
            if (data.key) {
                currentKey = data.key;
                document.getElementById('encryption-key').value = data.key;
                
                // Also update decryption key if the field exists
                const decryptionKey = document.getElementById('decryption-key');
                if (decryptionKey) decryptionKey.value = data.key;
            }
        })
        .catch(error => {
            showError('Error generating key: ' + error);
        });
}

// Toggle visibility of the encryption key
function toggleKeyVisibility() {
    const keyField = document.getElementById('encryption-key');
    if (keyField.type === 'password') {
        keyField.type = 'text';
    } else {
        keyField.type = 'password';
    }
}

// Create a new secure message
function createSecureMessage() {
    const message = document.getElementById('message-input').value;
    const key = document.getElementById('encryption-key').value;
    const expiryHours = document.getElementById('expiry-time').value;
    const maxViews = document.getElementById('max-views').value;

    if (!message) {
        showError('Please enter a message to encrypt!');
        return;
    }
    
    if (!key) {
        showError('Please generate an encryption key first!');
        return;
    }

    fetch(`${apiUrl}/encrypt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            message: message, 
            key: key,
            expiry_hours: parseInt(expiryHours),
            max_views: parseInt(maxViews)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message_id) {
            // Create shareable link
            const shareLink = `${window.location.origin}/message/${data.message_id}`;
            document.getElementById('share-link').value = shareLink;
            
            // Show success message
            document.getElementById('message-result').style.display = 'block';
            document.getElementById('create-message-panel').style.display = 'none';
            
            // Add to conversation list
            addToConversationsList(data.message_id, message.substring(0, 30));
            
            console.log("Message created with ID:", data.message_id);
        } else {
            showError('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error("Error during encryption:", error);
        showError('Error encrypting message: ' + error);
    });
}

// Copy share link to clipboard
function copyShareLink() {
    const shareLink = document.getElementById('share-link');
    shareLink.select();
    document.execCommand('copy');
    
    // Show copied notification
    const copyBtn = document.getElementById('copy-link-btn');
    const originalText = copyBtn.textContent;
    copyBtn.textContent = 'Copied!';
    setTimeout(() => {
        copyBtn.textContent = originalText;
    }, 2000);
}

// Check if we're viewing a shared message
function checkForSharedMessage() {
    const url = window.location.pathname;
    const messageIdMatch = url.match(/\/message\/([a-zA-Z0-9-]+)/);
    
    if (messageIdMatch && messageIdMatch[1]) {
        const messageId = messageIdMatch[1];
        loadSharedMessage(messageId);
    }
}

// Load a shared message
function loadSharedMessage(messageId) {
    // Show view message panel
    document.getElementById('create-message-panel').style.display = 'none';
    document.getElementById('view-message-panel').style.display = 'block';
    
    // Update title
    document.getElementById('current-chat-title').textContent = 'Secure Message';
    
    // Fetch message details
    fetch(`${apiUrl}/message/${messageId}`)
        .then(response => response.json())
        .then(data => {
            if (data.encrypted_message) {
                // Store the encrypted message for later decryption
                sessionStorage.setItem('currentEncryptedMessage', data.encrypted_message);
                sessionStorage.setItem('currentMessageId', messageId);
                
                // Update the status badges (if the API returns this info)
                if (data.views_left) {
                    document.getElementById('views-left-badge').textContent = 
                        `${data.views_left} view${data.views_left !== 1 ? 's' : ''} left`;
                }
                
                if (data.expires_in) {
                    document.getElementById('time-left-badge').textContent = 
                        `Expires in ${data.expires_in}`;
                }
            } else {
                showError('Error: ' + (data.error || 'Message not found'));
            }
        })
        .catch(error => {
            showError('Error loading message: ' + error);
        });
}

// Decrypt a message
function decryptMessage() {
    const encryptedMessage = sessionStorage.getItem('currentEncryptedMessage');
    const messageId = sessionStorage.getItem('currentMessageId');
    const key = document.getElementById('decryption-key').value;

    if (!encryptedMessage || !key) {
        showError('Encrypted message and key are required!');
        return;
    }

    fetch(`${apiUrl}/decrypt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            encrypted_message: encryptedMessage, 
            message_id: messageId,
            key: key 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.decrypted_message) {
            // Show decrypted message
            document.getElementById('encrypted-message-display').style.display = 'none';
            document.getElementById('decrypted-message-display').style.display = 'block';
            document.getElementById('decrypted-text').textContent = data.decrypted_message;
            
            // Update view count (if the message can be viewed multiple times)
            if (data.views_left) {
                document.getElementById('views-left-badge').textContent = 
                    `${data.views_left} view${data.views_left !== 1 ? 's' : ''} left`;
            } else {
                // If it's a one-time view, hide the decrypt button
                document.getElementById('decrypt-btn').style.display = 'none';
            }
        } else {
            showError('Error: ' + data.error);
        }
    })
    .catch(error => {
        showError('Error decrypting message: ' + error);
    });
}

// Add a message to the conversations list
function addToConversationsList(messageId, preview) {
    const conversationsList = document.getElementById('conversations-list');
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    // Create a new conversation element (using DOM methods instead of innerHTML)
    const newConvo = document.createElement('div');
    newConvo.className = 'friend-drawer friend-drawer--onhover';
    newConvo.setAttribute('data-message-id', messageId);
    
    newConvo.innerHTML = `
        <i class="material-icons profile-placeholder">mail</i>
        <div class="text">
            <h6>Secure Message</h6>
            <p class="text-muted">${preview}...</p>
        </div>
        <span class="time text-muted small">${timestamp}</span>
    `;
    
    // Create divider
    const divider = document.createElement('hr');
    
    // Add click handler for this new conversation
    newConvo.addEventListener('click', function() {
        // Highlight this conversation
        document.querySelectorAll('.friend-drawer--onhover').forEach(c => 
            c.classList.remove('active'));
        this.classList.add('active');
        
        // Load the message
        loadSharedMessage(messageId);
    });
    
    // Add to the conversations list
    conversationsList.insertBefore(divider, conversationsList.firstChild);
    conversationsList.insertBefore(newConvo, conversationsList.firstChild);
}

// Show error message
function showError(message) {
    // You can implement a toast notification or alert system
    console.error(message);
    alert(message);
}