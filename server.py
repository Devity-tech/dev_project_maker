import socket
import threading

LISTEN_ADDR = ("0.0.0.0", 8765)  # Exposed publicly (Render)

# Room dictionary: maps client socket -> room/session ID
rooms = {}
room_counter = 1
rooms_lock = threading.Lock()

def handle_client(client_socket, client_id):
    global room_counter
    # Assign a room/session
    with rooms_lock:
        room_id = room_counter
        rooms[client_socket] = room_id
        room_counter += 1

    print(f"[IWPS SERVER] New client connected, room {room_id}")

    # Receive initial target (for CONNECT tunneling)
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
        with rooms_lock:
            del rooms[client_socket]
        return

    print(f"[IWPS SERVER] Room {room_id} fetching: {host}:{port}")

    # Connect to the real server
    try:
        remote = socket.create_connection((host, port))
    except Exception as e:
        print(f"[!] Failed to connect {host}:{port} - {e}")
        client_socket.close()
        with rooms_lock:
            del rooms[client_socket]
        return

    # Start bidirectional piping
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
        with rooms_lock:
            rooms.pop(src, None)
        print(f"[IWPS SERVER] Room {room_id} closed")

def start_server():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(LISTEN_ADDR)
    listener.listen(100)
    print(f"[IWPS SERVER] Listening on {LISTEN_ADDR[0]}:{LISTEN_ADDR[1]}")

    client_id = 0
    while True:
        client_sock, addr = listener.accept()
        client_id += 1
        threading.Thread(target=handle_client, args=(client_sock, client_id), daemon=True).start()

if __name__ == "__main__":
    start_server()
