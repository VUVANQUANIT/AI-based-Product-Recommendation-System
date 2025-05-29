<?php
session_start();
require '/xampp/htdocs/WEB_LUANVAN/config/database.php';

if (!$conn) {
    die("Lỗi kết nối: " . mysqli_connect_error());
}

// Kiểm tra người dùng đã đăng nhập chưa
if (!isset($_SESSION['user_name'])) {
    echo "<p class='error'>Người Lut dùng chưa đăng nhập. Vui lòng đăng nhập để xem giỏ hàng.</p>";
    $conn->close();
    exit;
}

// Lấy user_id từ $_SESSION['user_name']
$user_name = $_SESSION['user_name'];
$user_id = $_SESSION['user_id'];
$sql_user = "SELECT user_id FROM users WHERE fullname = ?";
$stmt_user = $conn->prepare($sql_user);

if (!$stmt_user) {
    echo "<p class='error'>Lỗi chuẩn bị truy vấn user: " . $conn->error . "</p>";
    $conn->close();
    exit;
}

$stmt_user->bind_param("s", $user_name);
$stmt_user->execute();
$result_user = $stmt_user->get_result();

if ($result_user->num_rows === 0) {
    echo "<p class='error'>Không tìm thấy user_id.</p>";
    $stmt_user->close();
    $conn->close();
    exit;
}

$user_data = $result_user->fetch_assoc();
$user_id = $_SESSION['user_id'];
$stmt_user->close();

// Truy vấn giỏ hàng và kiểm tra tồn kho
$sql_cart = "
    SELECT c.cart_id, c.product_id, c.count AS cart_count, c.size, 
           p.product_name, p.price, p.image, p.count AS stock_count 
    FROM cart c
    JOIN product p ON c.product_id = p.product_id
    WHERE c.user_id = ?
";
$stmt_cart = $conn->prepare($sql_cart);

if (!$stmt_cart) {
    echo "<p class='error'>Lỗi chuẩn bị truy vấn cart: " . $conn->error . "</p>";
    $conn->close();
    exit;
}

$stmt_cart->bind_param("i", $user_id);
$stmt_cart->execute();
$result_cart = $stmt_cart->get_result();

$cart_items = [];
$total_amount = 0;

while ($row = $result_cart->fetch_assoc()) {
    $stock_count = $row['stock_count'];
    $cart_count = $row['cart_count'];

    // Kiểm tra nếu số lượng trong giỏ vượt quá tồn kho
    if ($cart_count > $stock_count) {
        $cart_count = $stock_count; // Giới hạn bằng tồn kho
    }

    $item_total = $row['price'] * $cart_count;
    $total_amount += $item_total;

    $cart_items[] = [
        "cart_id" => $row['cart_id'],
        "product_id" => $row['product_id'],
        "product_name" => $row['product_name'],
        "cart_count" => $cart_count,
        "size" => $row['size'],
        "price" => $row['price'],
        "image" => $row['image'],
        "stock_count" => $stock_count,
        "total" => $item_total
    ];
}

$stmt_cart->close();
$conn->close();

// Xuất HTML để nhúng
?>