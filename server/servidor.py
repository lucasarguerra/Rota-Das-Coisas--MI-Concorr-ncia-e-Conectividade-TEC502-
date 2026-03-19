import socket
import threading

valores = {}
lock = threading.Lock()

# Guarda a conexão do atuador (pode ser None se o atuador não conectou ainda)
conexao_atuador = None
lock_atuador = threading.Lock()  # lock separado para a conexão do atuador


# ── Funções UDP ──────────────────────────────────────────────────────────────

def tratar_sensor(data, addr):
    mensagem = data.decode()

    if ":" not in mensagem:
        print(f"Mensagem inválida de {addr}: {mensagem}")
        return

    tipo, valor = mensagem.split(":", 1)

    with lock:
        valores[tipo] = valor

    if tipo == "umidade":
        print(f"Umidade recebida: {valor}%")
    elif tipo == "temperatura":
        print(f"Temperatura recebida: {valor}°C")
    else:
        print(f"Dado desconhecido [{tipo}]: {valor}")


def tratar_comando(comando):
    """Recebe CMD:LIGAR ou CMD:DESLIGAR e repassa pro atuador via TCP."""
    global conexao_atuador

    # Extrai a ação: "CMD:LIGAR" → "LIGAR"
    acao = comando.split(":", 1)[1]

    with lock_atuador:
        if conexao_atuador is None:
            print("Nenhum atuador conectado. Comando ignorado.")
            return

        try:
            conexao_atuador.sendall(acao.encode())
            print(f"Comando '{acao}' enviado ao atuador.")

            # Aguarda confirmação do atuador
            confirmacao = conexao_atuador.recv(1024).decode()
            print(f"Atuador confirmou: {confirmacao}")

        except Exception as e:
            print(f"Erro ao comunicar com atuador: {e}")
            conexao_atuador = None  # marca como desconectado


# ── Servidor TCP (roda em thread separada) ───────────────────────────────────

def handle_atuador(conn, addr):
    """Fica vivo enquanto o atuador estiver conectado, detecta desconexão."""
    global conexao_atuador
    print(f"Atuador conectado: {addr}")

    # Fica em loop só para detectar se o atuador cair
    while True:
        try:
            # recv com timeout para não travar a thread para sempre
            conn.settimeout(2)
            data = conn.recv(1024)
            if not data:
                # Atuador fechou a conexão normalmente
                break
        except socket.timeout:
            # Timeout é normal, só continua esperando
            continue
        except Exception:
            break

    with lock_atuador:
        conexao_atuador = None
    conn.close()
    print(f"Atuador {addr} desconectado.")


def loop_tcp():
    """Aceita conexões TCP de atuadores. Roda em thread daemon."""
    global conexao_atuador

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.bind(('0.0.0.0', 12347))
    tcp_socket.listen(5)
    print("Servidor TCP aguardando atuadores na porta 12347...")

    while True:
        conn, addr = tcp_socket.accept()

        with lock_atuador:
            conexao_atuador = conn

        # Thread separada por atuador para detectar desconexão
        t = threading.Thread(target=handle_atuador, args=(conn, addr), daemon=True)
        t.start()


# ── Inicialização ─────────────────────────────────────────────────────────────

# Sobe o servidor TCP em background antes de entrar no loop UDP
thread_tcp = threading.Thread(target=loop_tcp, daemon=True)
thread_tcp.start()

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('0.0.0.0', 12345))
print("Servidor UDP aguardando na porta 12345...")

# ── Loop principal UDP ────────────────────────────────────────────────────────

while True:
    data, addr = udp_socket.recvfrom(1024)
    mensagem = data.decode()

    if mensagem.startswith("GET:"):
        tipo_pedido = mensagem.split(":", 1)[1]

        with lock:
            valor = valores.get(tipo_pedido)

        if valor:
            resposta = f"{tipo_pedido}: {valor}"
        else:
            resposta = f"Nenhum dado de {tipo_pedido} ainda"

        udp_socket.sendto(resposta.encode(), addr)

    elif mensagem.startswith("CMD:"):
        # Comando de controle: repassa pro atuador via TCP
        # Roda em thread para não bloquear o loop UDP enquanto espera confirmação
        thread_cmd = threading.Thread(
            target=tratar_comando,
            args=(mensagem,),
            daemon=True
        )
        thread_cmd.start()

    else:
        thread = threading.Thread(
            target=tratar_sensor,
            args=(data, addr),
            daemon=True
        )
        thread.start()
