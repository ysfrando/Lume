import base64
import os
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

logging.basicConfig(logging.INFO)
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
    # Decode the base64-encoded message
    encrypted_message_bytes = base64.b64decode(encrypted_message)
    
    # Extract the IV, tag, and ciphertext from the encrypted message
    iv = encrypted_message_bytes[:12] # First 12 bytes are the IV
    tag = encrypted_message_bytes[12:28] # Next 16 bytes are the tag
    ciphertext = encrypted_message_bytes[28:]
    
    # Create the AES-GCM cipher with the key and IV
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend)
    decryptor = cipher.decryptor()
    
    # Decrypt the ciphertext and return the decoded message
    decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()
    
    return decrypted_message.decode('utf-8')

# Test end-to-end
message = "Hello, this is a secure message."
key = generate_key()

# Encrypt the message
encrypted_message = encrypt_message(message, key)
print(f"Encrypted: {encrypted_message}")

# Decrypt the message
decrypted_message = decrypt_message(encrypted_message, key)
print(f"Decrypted: {decrypted_message}")

# Ensure the decrypted message matches the original
assert message == decrypted_message, "Decryption failed: The original and decrypted messages do not match!"
