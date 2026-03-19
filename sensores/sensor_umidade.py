import socket
import random
import time

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ('localhost', 12345)
while True:
    message = random.randint(0,100)
    message_str = f"umidade:{message}"

    udp_socket.sendto(message_str.encode(), address)
    print(f"Umidade enviada: {message}")
    


udp_socket.close()
