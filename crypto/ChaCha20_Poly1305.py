import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

NONCE_SIZE = 12


def encrypt(key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    chacha = ChaCha20Poly1305(key) # Create ChaCha20Poly1305 object with the given key
    nonce = os.urandom(NONCE_SIZE) # Generate a random nonce of the required size
    ct = chacha.encrypt(nonce, plaintext, aad) # Encrypt the plaintext with the nonce and optional AAD

    return nonce + ct

def decrypt(key: bytes, ct: bytes, aad: bytes = b"") -> bytes:
    chacha = ChaCha20Poly1305(key) # Create ChaCha20Poly1305 object with the given key
    nonce = ct[:NONCE_SIZE] # Extract the nonce from the beginning of the ciphertext
    ct = ct[NONCE_SIZE:] # The actual ciphertext is the remainder after the nonce

    return chacha.decrypt(nonce, ct, aad)
