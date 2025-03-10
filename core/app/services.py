"""
Cryptographic Services Module
============================

This module provides core cryptographic functions for secure message encryption and decryption
using AES-256 in Galois/Counter Mode (GCM).

Features:
- Secure cryptographic key generation
- Message encryption with AES-256-GCM
- Message decryption with authentication

Security features:
- Uses AES-256 for strong encryption
- GCM mode provides both confidentiality and authentication
- Unique initialization vector (IV) for each encryption
- Authentication tags to verify message integrity

This module should be used with the accompanying Flask API server.
"""

import base64
import os
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_key(key_length=32):
    """
    Generate a cryptographically secure random key.
    
    The default key length is 32 bytes (256 bits) which is suitable for AES-256.
    
    Args:
        key_length (int, optional): Length of the key in bytes. Defaults to 32.
        
    Returns:
        bytes: A randomly generated cryptographic key of specified length
        
    Raises:
        Exception: If key generation fails
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
    Encrypt a message using AES-256 in GCM mode.
    
    This function uses AES-256-GCM for authenticated encryption, which provides
    both confidentiality and integrity. A random 12-byte IV is generated for
    each encryption operation.
    
    Args:
        message (str): The plaintext message to encrypt
        key (bytes): The 32-byte (256-bit) encryption key
        
    Returns:
        str: Base64-encoded string containing IV + authentication tag + ciphertext
        
    Raises:
        ValueError: If message is empty
        Exception: If encryption fails for any other reason
    """
    if not message:
        raise ValueError("Message cannot be empty")
    
    try:
        # Generate a random 12-byte initialization vector (IV)
        iv = os.urandom(12)
        
        # Create a cipher object using AES algorithm with GCM mode
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        
        # Create an encryptor object
        encryptor = cipher.encryptor()
        
        # Encrypt the message
        ciphertext = encryptor.update(message.encode())
        ciphertext += encryptor.finalize()  # Finalize the encryption
        
        # Combine IV, authentication tag, and ciphertext
        encrypted_message = iv + encryptor.tag + ciphertext
        
        # Encode as Base64 for safe transmission
        return base64.b64encode(encrypted_message).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error encrypting message: {e}")
        raise

def decrypt_message(encrypted_message: str, key: bytes) -> str:
    """
    Decrypt a message that was encrypted using AES-256 in GCM mode.
    
    This function extracts the IV and authentication tag from the encrypted message
    and uses them with the provided key to authenticate and decrypt the ciphertext.
    
    Structure of encrypted_message after base64 decoding:
    - First 12 bytes: Initialization Vector (IV)
    - Next 16 bytes: Authentication Tag
    - Remaining bytes: Ciphertext
    
    Args:
        encrypted_message (str): Base64-encoded encrypted message
        key (bytes): The 32-byte (256-bit) decryption key
        
    Returns:
        str: The decrypted plaintext message
        
    Raises:
        ValueError: If key length is incorrect
        Exception: If decryption fails (returns error message instead of raising)
    """
    try:
        # Decode from Base64
        decoded_encrypted_message = base64.b64decode(encrypted_message)

        # Validate key length
        if len(key) != 32:
            raise ValueError(f"Key must be 32 bytes for AES-256, got {len(key)} bytes")

        # Extract components from the encrypted message
        iv = decoded_encrypted_message[:12]  # First 12 bytes are the IV
        tag = decoded_encrypted_message[12:28]  # Next 16 bytes are the authentication tag
        ciphertext = decoded_encrypted_message[28:]  # The rest is the ciphertext

        logger.info(f"IV length: {len(iv)}, Tag length: {len(tag)}, Ciphertext length: {len(ciphertext)}")

        # Create a cipher object with the extracted IV and tag
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the ciphertext
        decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

        # Convert from bytes to string
        return decrypted_message.decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error decrypting message: {e}")
        return f"Error: {str(e)}"