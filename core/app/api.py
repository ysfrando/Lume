"""
Encryption API Server
=====================

This Flask application provides a RESTful API for cryptographic operations including:
- Key generation
- Message encryption
- Message decryption

The server uses Base64 encoding for key transmission to ensure safe transport
of binary cryptographic keys over HTTP.

Endpoints:
----------
- GET /generate_key: Generate a new encryption key
- POST /encrypt: Encrypt a message using a provided key
- POST /decrypt: Decrypt a message using a provided key

Dependencies:
------------
- Flask: Web framework
- Flask-CORS: Cross-Origin Resource Sharing support
- services: Custom module containing cryptographic functions
"""

from flask import Blueprint, request, jsonify, render_template
from flask_cors import CORS
from .services import generate_key, encrypt_message, decrypt_message
from .models.message import Message
from .database import db  # Import the db instance
import logging
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint
app = Blueprint('api', __name__)

def decode_key(encoded_key):
    """Decode a Base64-encoded key into its binary form."""
    try:
        return base64.b64decode(encoded_key)
    except Exception as e:
        raise ValueError(f"Invalid key format: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_key', methods=["GET"])
def api_generate_key():
    """Generate a new cryptographic key."""
    try:
        key = generate_key()
        encoded_key = base64.b64encode(key).decode('utf-8')
        return jsonify({'key': encoded_key})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/encrypt', methods=["POST"])
def api_encrypt():
    """Encrypt a message and store it in the database with expiration settings."""
    try:
        data = request.get_json()
        message = data.get('message')
        encoded_key = data.get('key')
        expiry_hours = data.get('expiry_hours', 24)  # Default: 24 hours
        max_views = data.get('max_views', 1)  # Default: 1 view
        
        # Validate input parameters
        if not message or not encoded_key:
            return jsonify({'error': 'Message and key are required'}), 400
        
        # Decode the encryption key
        try:
            key = decode_key(encoded_key)
        except Exception as e:
            return jsonify({'error': f'Invalid key format: {str(e)}'}), 400
        
        # Perform encryption
        encrypted_message = encrypt_message(message, key)
        
        # Extract the IV from the encrypted message
        # In your implementation, the IV is the first 12 bytes of the base64-decoded message
        decoded_encrypted_message = base64.b64decode(encrypted_message)
        iv = base64.b64encode(decoded_encrypted_message[:12]).decode('utf-8')
        
        # Store in database
        message_id = Message.create_message(
            encrypted_content=encrypted_message,
            iv=iv,  # Pass the IV
            expiry_hours=expiry_hours,
            max_views=max_views
        )
        
        # Return message ID and encrypted message
        return jsonify({
            'message_id': message_id,
            'encrypted_message': encrypted_message,
            'expires_in': f"{expiry_hours} hours",
            'max_views': max_views
        }), 200

    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/message/<message_id>', methods=["GET"])
def get_message(message_id):
    """Retrieve a message by ID (doesn't decrypt it yet)."""
    try:
        message = Message.get_message(message_id)
        if not message:
            return jsonify({'error': 'Message not found or expired'}), 404
        
        encrypted_content = message
        return jsonify({
            'encrypted_message': encrypted_content,
            'message_id': message_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/decrypt', methods=["POST"])
def api_decrypt():
    """Decrypt an encrypted message using the provided key."""
    try:
        data = request.get_json()
        encrypted_message = data.get('encrypted_message')
        message_id = data.get('message_id')  # Optional: if decrypting from stored message
        encoded_key = data.get('key')
        
        # Validate input parameters
        if not encrypted_message or not encoded_key:
            return jsonify({'error': 'Encrypted message and key are required'}), 400
        
        # If message_id is provided, verify it exists and is still active
        if message_id:
            message = Message.get_message(message_id)
            if not message:
                return jsonify({'error': 'Message not found or expired'}), 404
            encrypted_message = message
        
        # Decode the decryption key
        try:
            key = decode_key(encoded_key)
        except Exception as e:
            return jsonify({'error': f'Invalid key format: {str(e)}'}), 400
        
        # Perform decryption
        decrypted_message = decrypt_message(encrypted_message, key)
        
        # Handle error response from decryption function
        if decrypted_message.startswith("Error:"):
            return jsonify({'error': decrypted_message}), 400
            
        return jsonify({'decrypted_message': decrypted_message}), 200
    
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return jsonify({'error': f"Decryption failed: {str(e)}"}), 400

# New endpoint for message cleanup (can be triggered manually or by scheduler)
@app.route('/admin/cleanup', methods=["POST"])
def cleanup_expired_messages():
    """Remove expired messages from the database."""
    try:
        deleted_count = Message.cleanup_expired()
        return jsonify({'success': True, 'deleted_count': deleted_count}), 200
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return jsonify({'error': str(e)}), 500