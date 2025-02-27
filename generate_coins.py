import mysql.connector
import hashlib
import time
import os
import json

# Conexão com o banco de dados
db = mysql.connector.connect(
    host="localhost",
    user="python_user",
    password="outra_senha_segura",
    database="game_wallet"
)
cursor = db.cursor()

# Função para gerar uma moeda única
def generate_unique_coin():
    coin_id = hashlib.sha256((str(time.time()) + str(os.urandom(16))).encode()).hexdigest()
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE amount = %s", (coin_id,))
    if cursor.fetchone()[0] == 0:
        return coin_id
    return generate_unique_coin()

# Função para atribuir moedas a um usuário
def generate_coins(user_address, amount):
    # Verificar se o usuário existe
    cursor.execute("SELECT id, balance FROM users WHERE address = %s", (user_address,))
    user = cursor.fetchone()
    if not user:
        print(f"Erro: Usuário com endereço {user_address} não encontrado.")
        return
    
    user_id, current_balance = user
    coin_value = float(amount)  # Valor da moeda em unidades do jogo
    
    # Registrar a geração como uma transação no banco (origem "system")
    cursor.execute(
        "INSERT INTO transactions (sender_id, receiver_address, amount, signature, status) VALUES (NULL, %s, %s, %s, %s)",
        (user_address, coin_value, "system_generated", "completed")
    )
    tx_id = cursor.lastrowid
    
    # Atualizar o saldo do usuário (convertendo Decimal para float)
    new_balance = float(current_balance) + coin_value
    cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, user_id))
    
    # Registrar na blockchain
    transaction = {
        "sender_address": "system",
        "receiver_address": user_address,
        "amount": coin_value,
        "tx_id": tx_id,
        "signature": "system_generated"
    }
    
    # Carregar ou iniciar a blockchain
    chain_file = "blockchain.json"
    if os.path.exists(chain_file):
        with open(chain_file, "r") as f:
            chain = json.load(f)
    else:
        chain = [{"index": 0, "previous_hash": "0", "timestamp": time.time(), "transaction": {"sender": "system", "receiver": "system", "amount": 0}, "nonce": 0, "hash": hashlib.sha256("genesis".encode()).hexdigest()}]
    
    # Adicionar novo bloco
    previous_block = chain[-1]
    new_block = {
        "index": len(chain),
        "previous_hash": previous_block["hash"],
        "timestamp": time.time(),
        "transaction": transaction,
        "nonce": 0
    }
    new_block["hash"] = hashlib.sha256(json.dumps(new_block, sort_keys=True).encode()).hexdigest()  # Hash simples para teste
    chain.append(new_block)
    
    # Salvar a blockchain
    with open(chain_file, "w") as f:
        json.dump(chain, f)
    
    db.commit()
    print(f"{coin_value} moedas geradas para {user_address}. Novo saldo: {new_balance}")

# Exemplo de uso
if __name__ == "__main__":
    user_address = input("Digite o endereço do usuário para receber moedas: ")
    amount = float(input("Quantas moedas gerar? "))
    generate_coins(user_address, amount)

db.close()
amount = input("Aperte Enter para finalizar: ")
