import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from services import generate_key, encrypt_message, decrypt_message
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def decode_key(encoded_key):
    try:
        return base64.b64decode(encoded_key)
    except Exception as e:
        raise ValueError(f"Invalid key format: {str(e)}")

@app.route('/generate_key', methods=["GET"])
def api_generate_key():
    try:
        key = generate_key()
        encoded_key = base64.b64encode(key).decode('utf-8')
        return jsonify({'key': encoded_key})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/encrypt', methods=["POST"])
def api_encrypt():
    try:
        data = request.get_json()
        message = data.get('message')
        encoded_key = data.get('key')
        
        if not message or not encoded_key:
            return jsonify({'error': 'Message and key are required'}), 400
        
        try:
            key = decode_key(encoded_key)
            logger.info(f"Key length after decode: {len(key)}")
        except Exception as e:
            return jsonify({'error': f'Invalid key format: {str(e)}'}), 400
        
        encrypted_message = encrypt_message(message, key)
        return jsonify({'encrypted_message': encrypted_message}), 200

    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/decrypt', methods=["POST"])
def api_decrypt():
    try:
        data = request.get_json()
        encrypted_message = data.get('encrypted_message')
        encoded_key = data.get('key')
        
        if not encrypted_message or not encoded_key:
            return jsonify({'error': 'Encrypted message and key are required'}), 400
        
        try:
            key = decode_key(encoded_key)
            logger.info(f"Key length after decode: {len(key)}")
        except Exception as e:
            return jsonify({'error': f'Invalid key format: {str(e)}'}), 400
        
        decrypted_message = decrypt_message(encrypted_message, key)
        
        if decrypted_message.startswith("Error:"):
            return jsonify({'error': decrypted_message}), 400
            
        return jsonify({'decrypted_message': decrypted_message}), 200
    
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return jsonify({'error': f"Decryption failed: {str(e)}"}), 400
    
if __name__ == '__main__':
    app.run(debug=True)
