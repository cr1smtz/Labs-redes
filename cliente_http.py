
import socket
import http.server



def http_get(path):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8000))

    request = (
        f"GET {path} HTTP/1.1\r\n"
        "Host: 127.0.0.1:8000\r\n"
        "\r\n"
    )

    client.sendall(request.encode('utf-8'))

    response = b""

    while True:
        data = client.recv(1024)
        if not data:
            break
        response += data

    client.close()
    return response.decode('utf-8')

def main():
    while True:
        print('Ingrese:\n"historial" para recibir el historial del chat"\n"usuarios" para recibir la lista de usaurios activos')
        request = input()
        print(http_get("/"+request))

main()
