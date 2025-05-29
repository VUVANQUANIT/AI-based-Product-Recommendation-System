<?php
$servername = "localhost";  // Tên máy chủ
$username = "root";         // Tên người dùng MySQL
$password = "";             // Mật khẩu MySQL (nếu có)
$dbname = "thoitrang";      // Tên cơ sở dữ liệu


$conn = new mysqli($servername, $username, $password, $dbname);


if ($conn->connect_error) {
    die("Kết nối thất bại: " . $conn->connect_error);
}

?>