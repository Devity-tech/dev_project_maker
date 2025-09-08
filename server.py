import socket
import threading

import os

PORT = int(os.getenv("PORT", 8765))
LISTEN_ADDR = ("0.0.0.0", PORT)

def handle_client(client_socket):
    # First line is target host:port
    target_line = b""
    while not target_line.endswith(b"\n"):
        chunk = client_socket.recv(1)
        if not chunk:
            client_socket.close()
            return
        target_line += chunk
    target_line = target_line.decode().strip()

    try:
        host, port = target_line.split(":")
        port = int(port)
    except:
        client_socket.close()
        return

    print(f"[IWPS SERVER] Fetching: {host}:{port}")

    # Connect to real target server
    try:
        remote = socket.create_connection((host, port))
    except Exception as e:
        print(f"[!] Failed to connect {host}:{port} - {e}")
        client_socket.close()
        return

    # Start bidirectional piping
    threading.Thread(target=pipe, args=(client_socket, remote)).start()
    threading.Thread(target=pipe, args=(remote, client_socket)).start()

def pipe(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        src.close()
        dst.close()

def start_server():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(LISTEN_ADDR)
    listener.listen(100)
    print(f"[IWPS SERVER] Listening on {LISTEN_ADDR[0]}:{LISTEN_ADDR[1]}")
    while True:
        client_sock, _ = listener.accept()
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    start_server()