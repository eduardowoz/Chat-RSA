import random
import hashlib
import requests
import sys
import argparse
import time
from threading import Thread
from flask import Flask, request

# --- INÍCIO DO MÓDULO DE CRIPTO MANUAL ---

def eh_primo(n, k=5):
    """ Testa se um número é provavelmente primo usando o teste de Miller-Rabin. """
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def gerar_primo(bits=256):
    """ Gera um número primo com uma quantidade específica de bits. """
    while True:
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1
        if eh_primo(n):
            return n

def mdc(a, b):
    """ Calcula o Máximo Divisor Comum usando o algoritmo de Euclides. """
    while b:
        a, b = b, a % b
    return a

def inverso_modular(a, m):
    """ Calcula o inverso modular de a (mod m) usando o Algoritmo Estendido de Euclides. """
    m0, x0, x1 = m, 0, 1
    if m == 1: return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0: x1 += m0
    return x1

def gerar_par_chaves(bits=256):
    """ Gera um par de chaves RSA (pública, privada). """
    p = gerar_primo(bits)
    q = gerar_primo(bits)
    while p == q:
        q = gerar_primo(bits)

    n = p * q
    phi = (p - 1) * (q - 1)
    
    e = 65537
    while mdc(e, phi) != 1:
        e = gerar_primo(16)

    d = inverso_modular(e, phi)
    
    return (n, e), (n, d)

def criptografar(mensagem_str, chave_publica):
    """ Criptografa uma mensagem string usando a chave pública. """
    n, e = chave_publica
    mensagem_int = int.from_bytes(mensagem_str.encode('utf-8'), 'big')
    return pow(mensagem_int, e, n)

def descriptografar(criptografado_int, chave_privada):
    """ Descriptografa um inteiro criptografado usando a chave privada. """
    n, d = chave_privada
    descriptografado_int = pow(criptografado_int, d, n)
    byte_array = descriptografado_int.to_bytes((descriptografado_int.bit_length() + 7) // 8, 'big')
    return byte_array.decode('utf-8')

def gerar_hash(mensagem):
    """ Gera um hash SHA-256 para a mensagem. """
    return hashlib.sha256(mensagem.encode('utf-8')).hexdigest()

def verificar_hash(mensagem, hash_recebido):
    """ Verifica se o hash de uma mensagem corresponde ao hash recebido. """
    hash_calculado = gerar_hash(mensagem)
    return hash_calculado == hash_recebido

# --- FIM DO MÓDULO DE CRIPTO MANUAL ---


# --- LÓGICA DO CHAT BIDIRECIONAL ---

app = Flask(__name__)

chave_publica_propria = None
chave_privada_propria = None
chave_publica_parceiro = None
username = "Anônimo"
url_parceiro = ""
handshake_concluido = False

@app.route('/get_public_key', methods=['GET'])
def get_public_key():
    return f"{chave_publica_propria[0]},{chave_publica_propria[1]}"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        dados_brutos = request.get_data(as_text=True)
        partes = dados_brutos.split('###')
        if len(partes) != 3: return "Formato inválido", 400

        remetente, criptografado_str, hash_recebido = partes
        criptografado_int = int(criptografado_str)
        mensagem = descriptografar(criptografado_int, chave_privada_propria)

        if not verificar_hash(mensagem, hash_recebido):
            print(f"\n!!! ALERTA: HASH INVÁLIDO da mensagem de {remetente}. MENSAGEM DESCARTADA. !!!")
            return "Hash inválido", 400
        
        print(f"\n[ {remetente} diz ]: {mensagem}")
        print(f"[{username}]: ", end="", flush=True)
        return "OK", 200

    except Exception as e:
        print(f"\n[ERRO NO WEBHOOK]: {e}")
        return "Erro", 500

def realizar_handshake():
    global chave_publica_parceiro, handshake_concluido
    print(f"\nTentando conectar com o parceiro em {url_parceiro}...")
    for tentativa in range(5):
        try:
            resposta = requests.get(f"{url_parceiro}/get_public_key", timeout=3)
            if resposta.status_code == 200:
                n_str, e_str = resposta.text.split(',')
                chave_publica_parceiro = (int(n_str), int(e_str))
                print("Conexão estabelecida e chave pública recebida!")
                handshake_concluido = True
                return
        except requests.exceptions.RequestException:
            print(f"Tentativa {tentativa+1}/5 falhou. Tentando novamente em 3 segundos...")
            time.sleep(3)
    
    print("\n[ERRO] Não foi possível conectar ao parceiro. Verifique o outro terminal.")
    sys.exit(1)

def enviar_mensagem(mensagem):
    if not handshake_concluido:
        print("Aguarde o handshake ser concluído antes de enviar mensagens.")
        return

    try:
        mensagem_criptografada = criptografar(mensagem, chave_publica_parceiro)
        hash_mensagem = gerar_hash(mensagem)
        
        # printar o texto criptografado 
        # print(f"[DEBUG] Texto Criptografado (nº inteiro) enviado: {mensagem_criptografada}")
        # #############################

        payload = f"{username}###{mensagem_criptografada}###{hash_mensagem}"
        headers = {'Content-Type': 'text/plain'}
        requests.post(f"{url_parceiro}/webhook", data=payload, headers=headers)
    except Exception as e:
        print(f"[X Erro ao enviar mensagem: {e}]")

def iniciar_servidor_flask(port):
    # Desativando o log padrão do Flask para uma saída mais limpa
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run(port=port, use_reloader=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chat P2P Criptografado com RSA Manual")
    parser.add_argument('--my-port', type=int, required=True, help="A porta que esta aplicação vai usar.")
    parser.add_argument('--peer-port', type=int, required=True, help="A porta da aplicação parceira.")
    parser.add_argument('--user', type=str, default="Anônimo", help="Seu nome de usuário.")
    args = parser.parse_args()

    username = args.user
    url_parceiro = f"http://127.0.0.1:{args.peer_port}"
    chave_publica_propria, chave_privada_propria = gerar_par_chaves()

    flask_thread = Thread(target=iniciar_servidor_flask, args=(args.my_port,))
    flask_thread.daemon = True
    flask_thread.start()

    print("="*50)
    print(f"      Chat iniciado para o usuário: {username}")
    print(f"      Ouvindo na porta: {args.my_port}")
    print("="*50)

    realizar_handshake()

    print("-"*50)
    print("Chat pronto! Digite sua mensagem e pressione Enter.")
    print("Digite 'sair' para fechar.")
    print("-"*50)

    while True:
        try:
            mensagem = input(f"[{username}]: ")
            if mensagem.lower() == 'sair':
                break
            if mensagem:
                enviar_mensagem(mensagem)
        except (KeyboardInterrupt, EOFError):
            break
    
    print("\nEncerrando o chat...")