import socket
import os
import mimetypes
from datetime import datetime

HOST, PORT = 'localhost', 8080
WWW_DIR = 'www'
LOG_FILE = 'server.log'

def log_request(method, path, status):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_type = "WARNING" if status.startswith("4") or status.startswith("5") else "INFO"
    log_message = f"[{timestamp}] [{log_type}] {method} request for {path} -> {status}"

    # Scrive nel file
    with open(LOG_FILE, 'a') as log:
        log.write(log_message + '\n')
    
    # Mostra anche nel terminale
    print(log_message)

def handle_request(client_socket):
    request = client_socket.recv(1024).decode('utf-8')
    lines = request.splitlines()
    if not lines:
        client_socket.close()
        return

    request_line = lines[0]
    try:
        method, path, _ = request_line.split()
    except ValueError:
        client_socket.close()
        return

    if method != 'GET':
        client_socket.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
        log_request(method, path, "405 Method Not Allowed")
        client_socket.close()
        return

    if path == '/':
        path = '/index.html'

    filepath = os.path.join(WWW_DIR, path.lstrip('/'))

    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            content = f.read()
        content_type, _ = mimetypes.guess_type(filepath)
        content_type = content_type or 'application/octet-stream'
        response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode('utf-8') + content
        log_request(method, path, "200 OK")
    else:
        response = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>"
        log_request(method, path, "404 Not Found")

    client_socket.sendall(response)
    client_socket.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)

        print(f"Server avviato su http://{HOST}:{PORT}")

        while True:
            client_conn, _ = server_socket.accept()
            handle_request(client_conn)

if __name__ == '__main__':
    run_server()