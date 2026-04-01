import socket
import threading
import datetime
import json
import http.server

host = '127.0.0.1'
port = 5500

PORT_UDP = 6500

udp_server_connect = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

lock = threading.Lock()
clients = []
nicknames = []
historial = []


#UDP
def mandar_logger(udp_socket, msj):
    udp_socket.sendto(msj.encode("utf-8"), (host, PORT_UDP))




#TCP

def enviar_mensaje(client, mensaje, cmd):
    data = {
        "cmd": cmd,
        "contenido": mensaje,
        "timestamp": datetime.datetime.now().isoformat()
    }

    serialized = json.dumps(data) + '\n'

    try:
        client.sendall(serialized.encode('utf-8'))

    except:
        pass





"""
recibir_mensaje(client,buffer):

Dado un objeto tipo socket client que es la abstraccion a cargo de la conexion con el cliente, recibe constantemente mensajes enviados (del tipo bytes object),
en caso de string vacio (cierre de conexion) retorna None, en caso de mensaje distinto de '', lo agrega a buffer para reconstruirlo.


"""
def recibir_mensaje(client,buffer):
    while True:
        data = client.recv(1024).decode('utf-8')

        if not data:
            return None, buffer

        buffer += data

        while '\n' in buffer:
            raw_msg, buffer = buffer.split('\n', 1)

            try:
                parsed = json.loads(raw_msg)
                with lock:
                    historial.append(parsed)
                return parsed, buffer
            except json.JSONDecodeError:
                continue



def broadcast(mensaje, cmd, lock, clients):

    copia_snapshot = []

    with lock:
        copia_snapshot = clients.copy()

    for client in copia_snapshot:
        enviar_mensaje(client, mensaje, cmd)


#########################################################
def consola_interna():
    while(True):
        print("Ingrese un comando:")
        comando = input()
        if comando == "HISTORIAL":
            with lock:
                for msg in historial:
                    print(msg)
                    
            
#HTTP

class MiHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/historial":
            with lock:
                data = json.dumps(historial)

            body = data.encode('utf-8')

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "\r\n"
            ).encode('utf-8') + body

            self.wfile.write(response)

        elif self.path == "/usuarios":
            with lock:
                data = json.dumps(nicknames)

            body = data.encode('utf-8')

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "\r\n"
            ).encode('utf-8') + body

            self.wfile.write(response)

        else:
            body = b'{"error": "Not found"}'

            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "\r\n"
            ).encode('utf-8') + body

            self.wfile.write(response)



def iniciar_http():
    httpd = http.server.HTTPServer((host, 8000), MiHandler)
    print("Servidor HTTP corriendo en puerto 8000")
    httpd.serve_forever()

#########################################################


def nuevo_cliente(client, address, clients, nicknames, historial, lock):
        
    print(f"Conectado con {address}")

    buffer = ""

    # Esperar NICK
    mensaje, buffer = recibir_mensaje(client, buffer)

    if mensaje is None:
        client.close()
        return

    if mensaje.get("cmd") != "NICK":
        client.close()
        return


    nickname = mensaje.get("contenido")

    with lock:

        # Validar nickname
        if nickname in nicknames:
            enviar_mensaje(client, "Nickname en uso", "ERROR")
            client.close()
            return

        nicknames.append(nickname)
        clients.append(client)
    
    enviar_mensaje(client, "Nickname registrado", "OK")
    print(f"Nickname registrado: {nickname}")
    broadcast(f"{nickname} joined!", "MSG", lock, clients)

    # ACA PONER SEND A UDP
    mandar_logger(udp_server_connect, f"CONNECT usuario={nickname} ip={address[0]}")


    # Ciclo que maneja interacciones con cliente
    while True:

        try:
            mensaje, buffer = recibir_mensaje(client, buffer)

            if mensaje is None:
                raise Exception("Cliente desconectado")


            cmd = mensaje.get("cmd")
            contenido = mensaje.get("contenido")
            data = {
                "cmd": cmd,
                "contenido": contenido,
                "timestamp": datetime.datetime.now().isoformat()
            }

            # Caso Mensaje
            if cmd == "MSG":
                print(f"{nickname} escribió: {contenido}")

                with lock:
                    historial.append(data)

                broadcast(f"{nickname}: {contenido}", "MSG", lock, clients)
                
                # ACÁ PONER SEND A UDP
                mandar_logger(udp_server_connect, f"MSG usuario={nickname} texto={contenido}")

            # Caso Desconexion
            elif cmd == "DISCONNECT":
                print(f"{nickname} se desconectó")
                enviar_mensaje(client,"Solicitud de desconexion recibida","DISCONNECT")
                with lock:
                    index = clients.index(client)
                    nick = nicknames[index]
                    clients.remove(client)
                    nicknames.remove(nick)

                client.close()
                broadcast(f"{nickname} abadonó el chat", "MSG", lock, clients)
                
                # ACÁ PONER SEND A UDP
                mandar_logger(udp_server_connect, f"DISCONNECT usuario={nickname} ip={address[0]}")

                return

                
        except Exception as e:
            
            with lock:
                if client in clients:

                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    nick = nicknames[index]
                    nicknames.remove(nick)

            client.close()
                    
            print(f"{nick} se cayó inesperadamente")
            broadcast(f"{nick} abandonó el chat inesperadamente!", "MSG", lock, clients)

            #ACÁ PONER SEND A UDP
            mandar_logger(udp_server_connect, f"ERROR usuario={nickname} motivo={e}")

            return






def receive(clients, nicknames, historial, lock):
    print("Servidor corriendo")


    while True:
        client, address = server.accept()

        thread_cliente = threading.Thread(target=nuevo_cliente, args=(client, address, clients, nicknames, historial, lock))
        thread_cliente.start()


 



thread_consola = threading.Thread(target=consola_interna, args=())
thread_consola.start()

thread_http = threading.Thread(target=iniciar_http, args=())
thread_http.start()



receive(clients, nicknames, historial, lock)