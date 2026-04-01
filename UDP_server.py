import socket
import threading
import datetime
import json
import os


HOST = "0.0.0.0"    
PORT = 6500       

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:

    server.bind((HOST, PORT))
    print(f"server UDP en {HOST}:{PORT}")

    with open("logger.log", "a") as file:

        while True:

            try:
                data, addr = server.recvfrom(65535)
                print(f"IP:{addr[0]}, Contenido: {data.decode('utf-8')}")
                file.write(data.decode('utf-8')+ "\n")
                
            except Exception as e:
                file.write(f"Error: {e}"+ "\n")


