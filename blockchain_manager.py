import hashlib
import json
import time
import mysql.connector
import os
from mnemonic import Mnemonic
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# Conexão com o banco
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="python_user",
        password="outra_senha_segura",
        database="game_wallet"
    )

# Classe para um bloco da blockchain
class Block:
    def __init__(self, index, previous_hash, timestamp, transaction, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transaction = transaction
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transaction": self.transaction,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

# Classe para a blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 2
        self.load_chain()

    def load_chain(self):
        if os.path.exists("blockchain.json"):
            with open("blockchain.json", "r") as f:
                loaded_chain = json.load(f)
                self.chain = [Block(
                    index=block["index"],
                    previous_hash=block["previous_hash"],
                    timestamp=block["timestamp"],
                    transaction=block["transaction"],
                    nonce=block["nonce"]
                ) for block in loaded_chain]
        else:
            self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", time.time(), {"sender_address": "system", "receiver_address": "system", "amount": "0.00"})
        self.chain.append(genesis_block)
        self.save_chain()

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, transaction):
        index = len(self.chain)
        previous_hash = self.get_latest_block().hash
        block = Block(index, previous_hash, time.time(), transaction)
        block.hash = self.mine_block(block)
        self.chain.append(block)
        self.save_chain()

    def mine_block(self, block):
        target = "0" * self.difficulty
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()
        return block.hash

    def save_chain(self):
        with open("blockchain.json", "w") as f:
            json.dump([vars(block) for block in self.chain], f)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def get_balance(self, address):
        balance = 0.0
        for block in self.chain:
            tx = block.transaction
            receiver = tx.get("receiver_address", tx.get("receiver", ""))
            sender = tx.get("sender_address", tx.get("sender", ""))
            amount = float(tx.get("amount", "0.00"))  # amount é string, converter para float
            if receiver == address:
                balance += amount
            if sender == address:
                balance -= amount
        return balance

# Função para verificar assinatura
def verify_signature(public_key_hex, signature_hex, message):
    try:
        public_key_hex = ''.join(public_key_hex.split())
        signature_hex = ''.join(signature_hex.split())
        
        if not all(c in '0123456789abcdefABCDEF' for c in public_key_hex):
            raise ValueError(f"Chave pública inválida: {public_key_hex}")
        if not all(c in '0123456789abcdefABCDEF' for c in signature_hex):
            raise ValueError(f"Assinatura inválida: {signature_hex}")
        
        public_key_bytes = bytes.fromhex(public_key_hex)
        signature_bytes = bytes.fromhex(signature_hex)
        # Verifica se message já é bytes, se não for, codifica
        if isinstance(message, bytes):
            message_bytes = message
        else:
            message_bytes = message.encode()
        
        public_key = serialization.load_der_public_key(public_key_bytes)
        public_key.verify(
            signature_bytes,
            message_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except (InvalidSignature, ValueError, TypeError) as e:
        print(f"Erro na verificação de assinatura: {e}")
        with open("C:\\xampp\\htdocs\\transactions.log", "a") as log:
            log.write(f"{time.ctime()} Erro na verificação: {e} (public_key={public_key_hex}, signature={signature_hex})\n")
        return False

# Função principal para processar transações e atualizar saldos
def process_blockchain():
    blockchain = Blockchain()
    db = get_db_connection()
    cursor = db.cursor()

    while True:
        print(f"Processando blockchain em {time.ctime()}...")

        if not blockchain.is_chain_valid():
            print("Atenção: Blockchain comprometida! Abortando processamento.")
            with open("C:\\xampp\\htdocs\\transactions.log", "a") as log:
                log.write(f"{time.ctime()}: Blockchain comprometida\n")
            break

        cursor.execute("SELECT id, sender_id, receiver_address, amount, signature FROM transactions WHERE status = 'pending'")
        transactions = cursor.fetchall()

        for tx in transactions:
            tx_id, sender_id, receiver_address, amount, signature = tx
            cursor.execute("SELECT balance, address, public_key FROM users WHERE id = %s", (sender_id,))
            sender_data = cursor.fetchone()
            if not sender_data:
                cursor.execute("UPDATE transactions SET status = 'failed' WHERE id = %s", (tx_id,))
                continue
            sender_balance, sender_address, sender_public_key = sender_data

            blockchain_balance = blockchain.get_balance(sender_address)
            
            # amount já é string no banco (ex.: "1000.00"), usar diretamente
            if blockchain_balance >= float(amount):
                cursor.execute("SELECT id FROM users WHERE address = %s", (receiver_address,))
                receiver = cursor.fetchone()
                if receiver:
                    receiver_id = receiver[0]
                    message = f"{sender_address}{receiver_address}{amount}".encode()  # amount como string
                    
                    if verify_signature(sender_public_key, signature, message):
                        transaction = {
                            "sender_address": sender_address,
                            "receiver_address": receiver_address,
                            "amount": amount,  # Salvar como string na blockchain
                            "tx_id": tx_id,
                            "signature": signature
                        }
                        blockchain.add_block(transaction)
                        cursor.execute("UPDATE transactions SET status = 'completed' WHERE id = %s", (tx_id,))
                        with open("C:\\xampp\\htdocs\\transactions.log", "a") as log:
                            log.write(f"{time.ctime()} Tx {tx_id}: {sender_address} -> {receiver_address}, {amount}, Block {blockchain.get_latest_block().index}\n")
                    else:
                        cursor.execute("UPDATE transactions SET status = 'failed' WHERE id = %s", (tx_id,))
                        with open("C:\\xampp\\htdocs\\transactions.log", "a") as log:
                            log.write(f"{time.ctime()} Tx {tx_id}: Assinatura inválida\n")
                else:
                    cursor.execute("UPDATE transactions SET status = 'failed' WHERE id = %s", (tx_id,))
            else:
                cursor.execute("UPDATE transactions SET status = 'failed' WHERE id = %s", (tx_id,))
                with open("C:\\xampp\\htdocs\\transactions.log", "a") as log:
                    log.write(f"{time.ctime()} Tx {tx_id}: Saldo insuficiente na blockchain ({blockchain_balance} < {amount})\n")

            db.commit()

        cursor.execute("SELECT id, address FROM users")
        users = cursor.fetchall()
        for user_id, address in users:
            true_balance = blockchain.get_balance(address)
            cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
            db_balance = float(cursor.fetchone()[0])
            if db_balance != true_balance:
                print(f"Correção: Usuário {address} - Saldo no banco ({db_balance}) ajustado para blockchain ({true_balance})")
                cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (true_balance, user_id))
                with open("C:\\xampp\\htdocs\\transactions.log", "a") as log:
                    log.write(f"{time.ctime()}: Saldo de {address} corrigido de {db_balance} para {true_balance}\n")
            db.commit()

        print("Blockchain válida e saldos sincronizados!")
        time.sleep(60)

    db.close()

if __name__ == "__main__":
    try:
        process_blockchain()
    except KeyboardInterrupt:
        print("Script encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        with open("C:\\xampp\\htdocs\\transactions.log", "a") as log:
            log.write(f"{time.ctime()}: Erro inesperado: {e}\n")
