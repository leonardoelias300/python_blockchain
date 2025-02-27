<?php
require 'config.php';

// Verificar logout
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: login.php');
    exit;
}

if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit;
}

$user_id = $_SESSION['user_id'];
$stmt = $db->prepare("SELECT username, balance, address FROM users WHERE id = ?");
$stmt->execute([$user_id]);
$user = $stmt->fetch();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Carteira do Jogo</title>
</head>
<body>
    <h1>Bem-vindo, <?php echo htmlspecialchars($user['username']); ?></h1>
    <p>Saldo: <?php echo htmlspecialchars($user['balance']); ?></p>
    <p>Seu endereço: <?php echo htmlspecialchars($user['address']); ?></p>
    
    <!-- Botão para enviar (abre send.php) -->
    <a href="send.php"><button>Enviar</button></a>
    
    <!-- Botão para receber (mantido como antes) -->
    <a href="receive.php"><button>Receber</button></a>
    
    <!-- Botão de logout -->
    <a href="index.php?logout=1"><button>Sair</button></a>
</body>
</html>