# Arquivo: ServidorA/security/crypto_manual.py

import random
import hashlib

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