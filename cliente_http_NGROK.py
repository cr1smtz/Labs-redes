import socket
import ssl


def http_get(path):
    host = "impressionless-bradyauxetically-tamala.ngrok-free.dev"

    raw_socket = socket.create_connection((host, 443))

    context = ssl.create_default_context()

    client = context.wrap_socket(raw_socket, server_hostname=host)

    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n"
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

    return response.decode('utf-8', errors="ignore")


def main():
    while True:
        print('Ingrese:\n"historial" para recibir el historial del chat\n"usuarios" para recibir la lista de usuarios activos')
        request = input()
        print(http_get("/" + request))


main()