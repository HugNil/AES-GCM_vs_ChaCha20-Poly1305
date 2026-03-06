import os
import struct
from dotenv import load_dotenv
import socket
from crypto.AES_GCM import encrypt as aes_encrypt, decrypt as aes_decrypt
from crypto.ChaCha20_Poly1305 import encrypt as chacha_encrypt, decrypt as chacha_decrypt


def recv_exact(conn: socket.socket, n: int) -> bytes:
    data = bytearray()
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data.extend(chunk)
    return bytes(data)


def recv_frame(conn: socket.socket) -> bytes:
    header = recv_exact(conn, 4)
    length = struct.unpack("!I", header)[0]
    return recv_exact(conn, length)


def send_frame(conn: socket.socket, payload: bytes):
    header = struct.pack("!I", len(payload))
    conn.sendall(header + payload)


def main():
    load_dotenv()

    algo = os.getenv("ALGO", "aes-gcm").lower()

    # Key: generate once per block (here read from .env as hex)
    key_hex = os.getenv("KEY_HEX")
    if key_hex:
        key = bytes.fromhex(key_hex)
    else:
        # fallback (ONLY for dev)
        key = b"12345678901234567890123456789012"

    if algo == "aes-gcm":
        encrypt_fn, decrypt_fn = aes_encrypt, aes_decrypt
    elif algo == "chacha20-poly1305":
        encrypt_fn, decrypt_fn = chacha_encrypt, chacha_decrypt
    else:
        raise ValueError("ALGO must be 'aes-gcm' or 'chacha20-poly1305'")

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5050))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port)) # Bind to the specified host and port
        server.listen(1) # Listen for incoming connections (max 1 queued connection)

        conn, addr = server.accept()

        with conn:
            while True:
                try:
                    encrypted_packet = recv_frame(conn)

                    # plaintext = decrypt(key, encrypted_packet)
                    plaintext = decrypt_fn(key, encrypted_packet)

                    # ack_packet = encrypt(key, ack_plaintext)
                    ack_plaintext = b"ACK"
                    ack_packet = encrypt_fn(key, ack_plaintext)

                    send_frame(conn, ack_packet)

                except ConnectionError:
                    break


if __name__ == "__main__":
    main()
