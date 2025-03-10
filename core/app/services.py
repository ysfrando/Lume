import base64
import os
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_key(key_length=32):
    """
    Generates a cryptographically secure random key for message encryption
    
    Args:
        key_length (int): Length of the key in bytes (default: 32 bytes / 256 bits)
        
    Returns:
        bytes: The generated key as bytes
    """
    try:
        key = os.urandom(key_length)
        logger.info(f"Generated key: {key}")
        return key
    except Exception as e:
        logger.error(f"Error generating key: {e}")
        raise

def encrypt_message(message: str, key: bytes) -> str:
    """
    Encrypts a given message using AES-GCM encryption and returns the encrypted message
    as a Base64-encoded string.

    AES-GCM (Galois/Counter Mode) provides both confidentiality (encryption) and 
    integrity (authentication) for the data.

    Args:
        message (str): The plaintext message to encrypt.
        key (bytes): The encryption key, should be 16, 24, or 32 bytes long (for AES-128, AES-192, or AES-256).

    Returns:
        str: The encrypted message, including IV, tag, and ciphertext, encoded in Base64.
        
    Raises:
        ValueError: If the key length is not 16, 24, or 32 bytes.
    """
    
    if not message:
        raise ValueError("Message cannot be empty")
    
    # Generate a random 12-byte Initialization Vector (IV) for AES-GCM
    try:
        iv = os.urandom(12)
        
        # Create the AES-GCM cipher using the provided key and generated IV
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        
        # Create an encryptor object to perform the encryption
        encryptor = cipher.encryptor()
        
        # Encrypt the message (convert the message to bytes and encrypt it)
        ciphertext = encryptor.update(message.encode())
        ciphertext += encryptor.finalize()  # Finalize the encryption
        
        # Combine the IV, authentication tag, and ciphertext to create the final encrypted message
        encrypted_message = iv + encryptor.tag + ciphertext
        
        # Return the Base64-encoded version of the encrypted message for safe storage/transmission
        return base64.b64encode(encrypted_message).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error encrypting message: {e}")
        raise

def decrypt_message(encrypted_message: str, key: bytes) -> str:
    """
    Decrypts a message that was encrypted with AES-GCM.
    
    Args:
        encrypted_message (str): Base64-encoded encrypted message
        key (bytes): The encryption key as bytes
        
    Returns:
        str: The decrypted message
    """
    try:
        # Decode the base64-encoded encrypted message
        decoded_encrypted_message = base64.b64decode(encrypted_message)

        # Verify the key length
        if len(key) != 32:
            raise ValueError(f"Key must be 32 bytes for AES-256, got {len(key)} bytes")

        # Extract IV and tag from the encrypted message
        iv = decoded_encrypted_message[:12]  # First 12 bytes are the IV
        tag = decoded_encrypted_message[12:28]  # Next 16 bytes are the tag
        ciphertext = decoded_encrypted_message[28:]  # Remaining bytes are the ciphertext

        logger.info(f"IV length: {len(iv)}, Tag length: {len(tag)}, Ciphertext length: {len(ciphertext)}")

        # Initialize the Cipher object with AES-GCM mode
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the ciphertext
        decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

        # Convert bytes to string and return
        return decrypted_message.decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error decrypting message: {e}")
        return f"Error: {str(e)}"