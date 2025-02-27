<?php
require 'config.php';

if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $user_id = $_SESSION['user_id'];
    $receiver_address = htmlspecialchars($_POST['receiver_address'], ENT_QUOTES, 'UTF-8');
    $amount = filter_input(INPUT_POST, 'amount', FILTER_VALIDATE_FLOAT); // Valida como float
    $amount_str = number_format($amount, 2, '.', ''); // Converte para string com 2 decimais
    $signature = trim($_POST['signature']);
    
    if (!ctype_xdigit($signature) || empty($signature)) {
        die("Erro: Assinatura inválida. Use apenas caracteres hexadecimais (0-9, a-f).");
    }
    
    if ($amount > 0 && $signature) {
        $stmt = $db->prepare("INSERT INTO transactions (sender_id, receiver_address, amount, signature) VALUES (?, ?, ?, ?)");
        $stmt->execute([$user_id, $receiver_address, $amount_str, $signature]);
        echo "Solicitação de envio registrada!";
    } else {
        echo "Dados inválidos!";
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Enviar Moedas</title>
</head>
<body>
    <form method="POST">
        Enviar para: <input type="text" name="receiver_address" required><br>
        Quantidade: <input type="number" name="amount" step="0.01" required><br>
        Assinatura: <input type="text" name="signature" required maxlength="144"><br>
        <input type="submit" value="Enviar">
    </form>
    <br>
    <a href="index.php"><button>Voltar</button></a>
</body>
</html>