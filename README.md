# Chat-RSA: Chat P2P com Criptografia Manual

Este projeto implementa um sistema de chat P2P (ponto-a-ponto) em Python, utilizando um algoritmo RSA implementado manualmente para criptografia de mensagens e o padrão SHA-256 para verificação de integridade.

A aplicação consiste em duas instâncias de servidor que se comunicam diretamente, trocando mensagens criptografadas em tempo real através de um terminal.

## Tecnologias Utilizadas
* **Python 3**
* **Flask:** Utilizado como um micro-servidor web para criar os *webhooks* que recebem as mensagens.
* **Requests:** Utilizado para a comunicação HTTP entre as duas instâncias do chat.
* **Criptografia Manual:** O algoritmo RSA (geração de chaves, criptografia e descriptografia) foi implementado do zero, sem o uso de bibliotecas de criptografia de alto nível.

## Estrutura do Projeto
```
Chat-RSA/
├── ServidorA/
│   ├── security/
│   │   └── crypto_manual.py  # Módulo com a lógica de cripto
│   └── app.py                # Aplicação principal do Servidor A
│
├── ServidorB/
│   ├── security/
│   │   └── crypto_manual.py  # Cópia do módulo de cripto
│   └── app.py                # Aplicação principal do Servidor B
│
├── iniciar.bat               # Script para iniciar os dois servidores (Windows)
└── requirements.txt          # Dependências do projeto
```

## Passo a Passo para Executar

### Pré-requisitos
- Python 3.7 ou superior instalado.

### 1. Preparação do Ambiente
Navegue até a pasta raiz do projeto (`Chat-RSA`) e instale as dependências necessárias com o seguinte comando:
```bash
pip install -r requirements.txt
```

### 2. Executando a Aplicação
Você pode iniciar o chat de duas maneiras:

**Método Automático (Windows)**
- Simplesmente dê um duplo-clique no arquivo `iniciar.bat`.
- Ele abrirá duas janelas de terminal separadas, uma para "Alice" (Servidor A) e outra para "Bob" (Servidor B), e iniciará o handshake automaticamente.

**Método Manual (Todos os Sistemas Operacionais)**
Você precisará de dois terminais abertos.

- **No Terminal 1:**
  ```bash
  # Navegue até a pasta do primeiro servidor
  cd Chat-RSA/ServidorA
  
  # Inicie o servidor A na porta 5000, se comunicando com a porta 5001
  python app.py --my-port 5000 --peer-port 5001 --user Alice
  ```

- **No Terminal 2:**
  ```bash
  # Navegue até a pasta do segundo servidor
  cd Chat-RSA/ServidorB
  
  # Inicie o servidor B na porta 5001, se comunicando com a porta 5000
  python app.py --my-port 5001 --peer-port 5000 --user Bob
  ```
Após a inicialização, os dois servidores realizarão o handshake e estarão prontos para trocar mensagens.

## Demonstrando a Criptografia

Para demonstrar o funcionamento da criptografia em tempo real, o código está preparado para exibir o texto criptografado no terminal.

1.  Abra o arquivo `app.py` (em qualquer um dos servidores, pois são idênticos).
2.  Navegue até a função `enviar_mensagem`.
3.  Você encontrará a seguinte seção no código:

    ```python
    # printar o texto criptografado !!##
    # print(f"[DEBUG] Texto Criptografado (nº inteiro) enviado: {mensagem_criptografada}")
    # ######################################################################################
    ```
4.  Para ativar a funcionalidade, simplesmente **remova o `#`** do início da linha do `print` e salve o arquivo.
5.  Pare o servidor que você modificou (`CTRL+C`) e rode-o novamente com o mesmo comando.
6.  Ao enviar uma nova mensagem, o texto criptografado (em formato de número inteiro) será exibido no terminal do remetente antes de ser enviado.
