<?php
require 'config.php';

// Ativar exibição de erros para depuração
error_reporting(E_ALL);
ini_set('display_errors', 1);

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = htmlspecialchars($_POST['username'], ENT_QUOTES, 'UTF-8');
    $password = password_hash($_POST['password'], PASSWORD_BCRYPT);
    
    // Gerar seed phrase
    $python_path = 'C:\\Program Files\\Python313\\python.exe'; // Caminho confirmado
    $seed_script = __DIR__ . DIRECTORY_SEPARATOR . 'generate_seed.py';
    $seed_command = "\"$python_path\" \"$seed_script\" 2>&1";
    $seed_output = shell_exec($seed_command);
    $seed_phrase = $seed_output !== null ? trim($seed_output) : '';
    
    if (empty($seed_phrase) || strpos($seed_output, 'Traceback') !== false) {
        die("Erro: Não foi possível gerar a seed phrase. Comando: $seed_command, Saída: " . htmlspecialchars($seed_output));
    }
    
    // Gerar chave pública a partir da seed phrase
    $key_script = __DIR__ . DIRECTORY_SEPARATOR . 'generate_keypair.py';
    $key_command = "\"$python_path\" \"$key_script\" \"$seed_phrase\" 2>&1";
    $key_output = shell_exec($key_command);
    $public_key = $key_output !== null ? trim($key_output) : '';
    
    // Validar que a chave pública é hexadecimal
    if (empty($public_key) || !ctype_xdigit($public_key) || strpos($key_output, 'Traceback') !== false) {
        die("Erro: Chave pública inválida. Comando: $key_command, Saída: " . htmlspecialchars($key_output));
    }
    
    $address = hash('sha256', uniqid($username . time(), true));
    
    $stmt = $db->prepare("INSERT INTO users (username, password, address, public_key) VALUES (?, ?, ?, ?)");
    if ($stmt->execute([$username, $password, $address, $public_key])) {
        echo "Usuário cadastrado!<br>";
        echo "Seu endereço: $address<br>";
        echo "Seed Phrase (anote e guarde em segurança, nunca compartilhe): $seed_phrase<br>";
    } else {
        echo "Erro ao cadastrar!";
    }
}
?>
<form method="POST">
    Usuário: <input type="text" name="username" required><br>
    Senha: <input type="password" name="password" required><br>
    <input type="submit" value="Cadastrar">
</form>