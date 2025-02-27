import secrets

# Lista simples de palavras para teste (pode usar BIP-39 em produção)
word_list = ["apple", "banana", "cat", "dog", "elephant", "fish", "grape", "horse", "ice", "jungle", "kite", "lemon"]

# Gerar 12 palavras aleatórias
seed_phrase = " ".join(secrets.choice(word_list) for _ in range(12))
print(seed_phrase)