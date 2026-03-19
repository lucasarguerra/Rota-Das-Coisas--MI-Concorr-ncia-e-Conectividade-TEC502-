import socket

loop = True

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # linha adicionada
address = ('localhost', 12345)
udp_socket.bind(('0.0.0.0', 12346))
udp_socket.settimeout(5)

print("SISTEMA ROTA DAS COISAS: IOT")
input("Clique enter para a abertura do menu principal")

while loop:
    print("=" * 14)
    print("MENU PRINCIPAL")
    print("=" * 14)
    print("[1] Consultar valor atual dos sensores")
    print("[2] Enviar comando pros atuadores")
    print("[3] Sair do sistema")
    option = input("Digite aqui: ")

    if option == "1":
        print("Qual sensor deseja consultar?")
        print("[1] Temperatura")
        print("[2] Umidade")
        sensor_option = input("Digite aqui: ")

        if sensor_option == "1":
            tipo = "temperatura"
        elif sensor_option == "2":
            tipo = "umidade"
        else:
            print("Opção inválida.")
            continue

        udp_socket.sendto(f"GET:{tipo}".encode(), address)

        try:
            data, addr = udp_socket.recvfrom(1024)
            print("Valor atual:", data.decode())
        except socket.timeout:
            print("Servidor não respondeu. Verifique se está rodando.")

    elif option == "2":
        print("O que você deseja fazer com o atuador?")
        print("[1] Ligar")
        print("[2] Desligar")
        option_2 = input("Digite aqui: ")

        if option_2 == "1":
            udp_socket.sendto("CMD:LIGAR".encode(), address)
            print("Comando LIGAR enviado.")
        elif option_2 == "2":
            udp_socket.sendto("CMD:DESLIGAR".encode(), address)
            print("Comando DESLIGAR enviado.")
        else:
            print("Opção inválida.")

    elif option == "3":
        print("Encerrando sistema...")
        loop = False
    else:
        print("Você digitou um comando inexistente, tente novamente.")

udp_socket.close()
