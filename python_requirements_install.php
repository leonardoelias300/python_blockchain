<?php
require 'config.php';
$version_output = shell_exec("python.exe -m pip install mnemonic cryptography 2>&1");
echo "Python: " . htmlspecialchars($version_output) . "";
?>

