import socket
import random
import time

# Criação do objeto socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Endereço e porta de destino
address = ('localhost', 12345)

while True:
    # Entrada dos dados a serem enviados
    message = random.randint(0,100)
    message_str = f"temperatura:{message}"
    

    # Envio dos dados
    udp_socket.sendto(message_str.encode(), address)
    print(f"Temperatura enviada: {message}")
    

# Fechamento do socket
udp_socket.close()
