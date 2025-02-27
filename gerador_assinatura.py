from mnemonic import Mnemonic
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

seed_phrase = input("Digite sua seed phrase (12 palavras): ")
sender_address = input("Seu endereço: ")
receiver_address = input("Endereço do destinatário: ")
amount = input("Quantidade (ex.: 1000.00): ")

mnemo = Mnemonic("english")
seed = mnemo.to_seed(seed_phrase)
private_key = ec.derive_private_key(int.from_bytes(seed[:32], 'big'), ec.SECP256K1())

message = f"{sender_address}{receiver_address}{amount}".encode()
signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
signature_hex = signature.hex()

print(f"Assinatura: {signature_hex}")
amount = input("Aperte Enter para finalizar: ")