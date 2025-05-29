<?php
session_start();
define('BASE_PATH', dirname(__DIR__));
require '/xampp/htdocs/WEB_LUANVAN/config/database.php';
header('Content-Type: application/json');

if (!isset($_SESSION['user_id']) || !is_numeric($_SESSION['user_id'])) {
    echo json_encode(["status" => "error", "message" => "Bạn cần đăng nhập để mua hàng."]);
    exit;
}

$user_id = (int)$_SESSION['user_id'];
$product_id = isset($_POST['product_id']) ? (int)$_POST['product_id'] : null;
$count = isset($_POST['quantity']) ? (int)$_POST['quantity'] : 1;
$size = $_POST['size'] ?? null;

if (!$product_id || $product_id <= 0 || $count <= 0 || !$size) {
    echo json_encode(["status" => "error", "message" => "Dữ liệu không hợp lệ."]);
    exit;
}

// Kiểm tra sản phẩm trong giỏ hàng với kích cỡ
$sql = "SELECT COUNT(*) FROM cart WHERE user_id = ? AND product_id = ? AND size = ?";
$stmt = $conn->prepare($sql);
if (!$stmt) {
    echo json_encode(["status" => "error", "message" => "Lỗi kết nối cơ sở dữ liệu: " . $conn->error]);
    exit;
}
$stmt->bind_param("iis", $user_id, $product_id, $size);
$stmt->execute();
$result = $stmt->get_result()->fetch_row()[0];

if ($result > 0) {
    $sql = "UPDATE cart SET count = count + ? WHERE user_id = ? AND product_id = ? AND size = ?";
    $stmt = $conn->prepare($sql);
    if (!$stmt) {
        echo json_encode(["status" => "error", "message" => "Lỗi chuẩn bị câu lệnh: " . $conn->error]);
        exit;
    }
    $stmt->bind_param("iiis", $count, $user_id, $product_id, $size);
} else {
    $sql = "INSERT INTO cart (user_id, product_id, count, size) VALUES (?, ?, ?, ?)";
    $stmt = $conn->prepare($sql);
    if (!$stmt) {
        echo json_encode(["status" => "error", "message" => "Lỗi chuẩn bị câu lệnh: " . $conn->error]);
        exit;
    }
    $stmt->bind_param("iiis", $user_id, $product_id, $count, $size);
}

if ($stmt->execute()) {
    echo json_encode(["status" => "success", "message" => "Sản phẩm đã được thêm vào giỏ hàng!"]);
} else {
    echo json_encode(["status" => "error", "message" => "Lỗi khi thêm sản phẩm: " . $stmt->error]);
}

$stmt->close();
$conn->close();
?>