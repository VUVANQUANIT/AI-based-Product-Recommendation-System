<?php
session_start();
header("Content-Type: application/json");
ini_set('display_errors', 1);
error_reporting(E_ALL);

$servername = "localhost"; 
$username = "root";        
$password = "";             
$dbname = "thoitrang";      

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die(json_encode(["status" => "error", "message" => "Kết nối thất bại: " . $conn->connect_error]));
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(["status" => "error", "message" => "Yêu cầu không hợp lệ!"]);
    exit;
}

$emailOrPhone = isset($_POST['loginInput']) ? trim($_POST['loginInput']) : null;
$password = isset($_POST['password']) ? $_POST['password'] : null;

if (!$emailOrPhone || !$password) {
    echo json_encode(["status" => "error", "message" => "Vui lòng nhập đủ thông tin!"]);
    exit;
}

$query = "SELECT user_id, pass,fullname,email FROM users WHERE email = ? OR phone = ?";
$stmt = $conn->prepare($query);
$stmt->bind_param("ss", $emailOrPhone, $emailOrPhone);
$stmt->execute();
$result = $stmt->get_result();
$user = $result->fetch_assoc();

if (!$user) {
    echo json_encode(["status" => "error", "message" => "Tài khoản không tồn tại!"]);
    exit;
}

if ($password !== $user['pass']) {
    echo json_encode(["status" => "error", "message" => "Sai mật khẩu!"]);
    exit;
}

$_SESSION['user_id'] = $user['user_id'];
$_SESSION['user_name'] = $user['fullname'];
$_SESSION['user_email'] = $user['email'];


echo json_encode(["status" => "OK", "message" => "Đăng nhập thành công!"]);
?>
