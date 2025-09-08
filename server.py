import socket
import threading
import os

PORT = int(os.getenv("PORT", 8765))
LISTEN_ADDR = ("0.0.0.0", PORT)

# Your existing server code...

# Predefined users (username:password)
USERS = {
    "alice": "pass123",
    "bob": "mypassword",
}

# Mapping: username -> room_id
rooms_by_user = {}
room_counter = 1
rooms_lock = threading.Lock()

# Mapping: client socket -> username
clients = {}

def handle_client(client_socket, addr):
    global room_counter

    # Step 1: Receive username:password
    try:
        auth_line = client_socket.recv(1024).decode().strip()
        if not auth_line or ":" not in auth_line:
            client_socket.close()
            return
        username, password = auth_line.split(":", 1)
    except:
        client_socket.close()
        return

    # Step 2: Validate credentials
    if username not in USERS or USERS[username] != password:
        print(f"[IWPS SERVER] Invalid login from {addr}")
        client_socket.close()
        return

    # Step 3: Assign/reuse room
    with rooms_lock:
        if username in rooms_by_user:
            room_id = rooms_by_user[username]
            print(f"[IWPS SERVER] Existing user reconnecting: {username}, room {room_id}")
        else:
            room_id = room_counter
            rooms_by_user[username] = room_id
            room_counter += 1
            print(f"[IWPS SERVER] New user connected: {username}, room {room_id}")

        clients[client_socket] = username

    # Step 4: Receive target host:port
    target_line = b""
    while not target_line.endswith(b"\n"):
        chunk = client_socket.recv(1)
        if not chunk:
            break
        target_line += chunk
    target_line = target_line.decode().strip()

    try:
        host, port = target_line.split(":")
        port = int(port)
    except:
        client_socket.close()
        cleanup(client_socket)
        return

    print(f"[IWPS SERVER] Room {room_id} fetching: {host}:{port}")

    # Step 5: Connect to real server
    try:
        remote = socket.create_connection((host, port))
    except Exception as e:
        print(f"[!] Failed to connect {host}:{port} - {e}")
        client_socket.close()
        cleanup(client_socket)
        return

    # Step 6: Start bidirectional piping
    threading.Thread(target=pipe, args=(client_socket, remote, room_id), daemon=True).start()
    threading.Thread(target=pipe, args=(remote, client_socket, room_id), daemon=True).start()

def pipe(src, dst, room_id):
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
        cleanup(src)
        print(f"[IWPS SERVER] Room {room_id} closed connection")

def cleanup(client_socket):
    with rooms_lock:
        username = clients.get(client_socket)
        if username:
            # Keep room persistent
            clients.pop(client_socket, None)

def start_server():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(LISTEN_ADDR)
    listener.listen(100)
    print(f"[IWPS SERVER] Listening on {LISTEN_ADDR[0]}:{LISTEN_ADDR[1]}")

    while True:
        client_sock, addr = listener.accept()
        threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()