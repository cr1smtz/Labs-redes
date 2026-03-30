
import socket
import threading
import datetime
import json

def recibir_mensaje(client, buffer):
    while True:
        data = client.recv(1024).decode('utf-8')

        if not data:
            return None, buffer  # conexión cerrada

        buffer += data

        while '\n' in buffer:
            raw_msg, buffer = buffer.split('\n', 1)

            try:
                parsed = json.loads(raw_msg)
                print(parsed)
                return parsed, buffer
            except json.JSONDecodeError:
                print("Mensaje JSON inválido recibido")
                continue

def enviar_mensaje(client,mensaje,cmd):  
    data = {
        "cmd": cmd,
        "contenido": mensaje,
        "timestamp": datetime.datetime.now().isoformat()
    }

    serialized = json.dumps(data) + '\n'

    try:
        client.sendall(serialized.encode('utf-8'))
    except:
        print("Error enviando mensaje")

def escribir_chat(client,estado):
    while(estado["conexion"]):
        print("Escribe algo:")
        chat = input()
        if(chat!="DISCONNECT"):
            enviar_mensaje(client,chat,"MSG")
        else:
            enviar_mensaje(client,chat,"DISCONNECT")

    if not estado["conexion"]:
        print("Chat desconectado")        

def registro():
    flag = False
    while not(flag):
        buffer = ""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 5500))
        print("Ingrese su nombre de usuario:")
        nombre = input()
        enviar_mensaje(client,nombre,"NICK")
        respuesta,buffer = recibir_mensaje(client,buffer)

        if(respuesta is None):
            print("Servidor cerró la conexión")
            client.close()
            continue    
        elif(respuesta.get("cmd")=="OK"):
            print("Usuario registrado correctamente")
            estado["conexion"] = True
            return client,buffer
        else:
            print("Error, nombre de Usuario ocupado, intente nuevamente")
            client.close()
            buffer = ""


def usuario_escuchando(client,buffer,estado):
    while estado["conexion"]:
        mensaje,buffer = recibir_mensaje(client,buffer)
        
        if mensaje is None:
            estado["conexion"] = False
            break

        cmd = mensaje.get('cmd')

        if cmd == "MSG":
            print(mensaje.get('contenido'))

        elif cmd == "DISCONNECT":
            print("Saliste del chat")
            estado["conexion"] = False
            client.close()
            
            



estado = {"conexion": False}
    
client,buffer = registro()

listen_thread = threading.Thread(target=usuario_escuchando, args=(client,buffer,estado))
listen_thread.start()

write_thread = threading.Thread(target=escribir_chat, args=(client,estado))
write_thread.start()

 

