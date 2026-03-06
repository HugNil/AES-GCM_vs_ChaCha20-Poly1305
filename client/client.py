import os
import socket
import struct
import time
import csv
from dotenv import load_dotenv

from crypto.AES_GCM import encrypt as aes_encrypt, decrypt as aes_decrypt
from crypto.ChaCha20_Poly1305 import encrypt as chacha_encrypt, decrypt as chacha_decrypt
from client.message_generator import make_json_message_exact_size


def recv_exact(conn: socket.socket, n: int) -> bytes:
    """
    Read exactly n bytes from the connection.
    This handles cases where recv() returns less than n bytes.
    """
    data = bytearray()
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data.extend(chunk)
    return bytes(data)


def recv_frame(conn: socket.socket) -> bytes:
    """
    Read a framed message from the connection.
    The frame format is:
    [4 bytes big-endian length][payload bytes]
    """
    header = recv_exact(conn, 4)
    length = struct.unpack("!I", header)[0]
    if length <= 0 or length > 10_000_000:
        raise ValueError(f"Invalid frame length: {length}")
    return recv_exact(conn, length)


def send_frame(conn: socket.socket, payload: bytes):
    """
    Send a framed message over the connection.
    The frame format is:
    [4 bytes big-endian length][payload bytes]
    """
    header = struct.pack("!I", len(payload))
    conn.sendall(header + payload)


def main():
    """
    Main function to run the client.
    It connects to the server, sends encrypted messages of varying sizes,
    and measures the latency of each operation.
    The results are saved to a CSV file for analysis.
    Configuration is done via environment variables.
    """
    load_dotenv()

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5050"))

    algo = os.getenv("ALGO", "aes-gcm").lower()
    runs = int(os.getenv("RUNS", "1000"))
    warmup = int(os.getenv("WARMUP", "100"))
    block_id = os.getenv("BLOCK_ID", "1")

    # Three fixed message sizes
    msg_sizes = [
        int(os.getenv("MSG_SMALL", "128")),
        int(os.getenv("MSG_MEDIUM", "512")),
        int(os.getenv("MSG_LARGE", "2048")),
    ]

    # Key: generate once per block (here read from .env as hex)
    key_hex = os.getenv("KEY_HEX")
    if key_hex:
        key = bytes.fromhex(key_hex)
    else:
        # fallback (ONLY for dev)
        key = b"12345678901234567890123456789012"

    # Pick algorithm functions once
    if algo == "aes-gcm":
        encrypt_fn, decrypt_fn = aes_encrypt, aes_decrypt
    elif algo == "chacha20-poly1305":
        encrypt_fn, decrypt_fn = chacha_encrypt, chacha_decrypt
    else:
        raise ValueError("ALGO must be 'aes-gcm' or 'chacha20-poly1305'")

    # Prepare plaintext payloads ONCE per message size
    plaintext_by_size = {s: make_json_message_exact_size(s) for s in msg_sizes}

    # Write results to CSV for analysis
    os.makedirs("results", exist_ok=True)
    out_path = os.path.join("results", f"latency_{algo}_block{block_id}.csv")

    rows = [] # List to hold result rows before writing to CSV

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        conn.connect((host, port)) # Connect to the server

        for size in msg_sizes: # Loop over each message size
            plaintext = plaintext_by_size[size]

            # Warm-up (NOT measured)
            for _ in range(warmup):
                pkt = encrypt_fn(key, plaintext)
                send_frame(conn, pkt)
                ack_pkt = recv_frame(conn)
                _ = decrypt_fn(key, ack_pkt)

            # Measured runs
            for i in range(runs):
                t0 = time.perf_counter_ns() # Start timer

                pkt = encrypt_fn(key, plaintext) # Encrypt the plaintext using the selected algorithm
                send_frame(conn, pkt) # Send the encrypted packet to the server using the framing protocol
                ack_pkt = recv_frame(conn) # Wait for the ACK from the server
                _ = decrypt_fn(key, ack_pkt) # Decrypt the ACK to ensure the round-trip is complete

                t1 = time.perf_counter_ns() # End timer

                rows.append( # Append the result of this iteration to the rows list
                    {
                        "algorithm": algo,
                        "message_size_bytes": size,
                        "iteration": i,
                        "latency_ns": t1 - t0,
                    }
                )

    with open(out_path, "w", newline="", encoding="utf-8") as f: # Write the collected results to a CSV file
        writer = csv.DictWriter(
            f,
            fieldnames=["algorithm", "message_size_bytes", "iteration", "latency_ns"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()