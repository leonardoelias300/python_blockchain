<?php
session_start();
$db = new PDO('mysql:host=localhost;dbname=game_wallet', 'php_user', 'senha_segura');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
?>