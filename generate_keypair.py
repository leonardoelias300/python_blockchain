import sys
from mnemonic import Mnemonic
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Receber seed phrase como argumento
seed_phrase = sys.argv[1] if len(sys.argv) > 1 else "apple banana cat dog elephant fish grape horse ice jungle kite lemon"

# Gerar chave privada a partir da seed
mnemo = Mnemonic("english")
seed = mnemo.to_seed(seed_phrase)
private_key = ec.derive_private_key(int.from_bytes(seed[:32], 'big'), ec.SECP256K1())

# Gerar chave pública
public_key = private_key.public_key()
public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Saída: chave pública em hex
print(public_key_bytes.hex())