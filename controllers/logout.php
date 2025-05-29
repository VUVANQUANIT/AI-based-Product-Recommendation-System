<?php
session_start(); // Bắt đầu session

// Xóa toàn bộ session
$_SESSION = [];
session_destroy();

// Chuyển hướng về trang chủ
header("Location: /WEB_LUANVAN/index.php");
exit();
?>
