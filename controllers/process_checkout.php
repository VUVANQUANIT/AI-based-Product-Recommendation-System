<?php
session_start();
require "/xampp/htdocs/WEB_LUANVAN/config/database.php";

if (!isset($_SESSION['user_id'])) {
    header("Location: ../signin.php");
    exit();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $user_id = $_SESSION['user_id'];
    $payment_method = $_POST['payment_method'] ?? 'cod';

    // Load giỏ hàng
    $sql = "SELECT c.cart_id, c.product_id, c.count, c.size, p.price, p.product_name, p.count AS stock 
            FROM cart c 
            JOIN product p ON c.product_id = p.product_id 
            WHERE c.user_id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $user_id);
    $stmt->execute();
    $result = $stmt->get_result();
    $cart_items = $result->fetch_all(MYSQLI_ASSOC);

    if (empty($cart_items)) {
        echo json_encode(['success' => false, 'message' => 'Giỏ hàng trống']);
        exit();
    }

    // Kiểm tra tồn kho
    foreach ($cart_items as $item) {
        if ($item['count'] > $item['stock']) {
            echo json_encode(['success' => false, 'message' => "Sản phẩm {$item['product_name']} không đủ hàng (còn {$item['stock']})"]);
            $conn->close();
            exit();
        }
    }

    // Tính tổng tiền
    $total_amount = 0;
    foreach ($cart_items as $item) {
        $total_amount += $item['price'] * $item['count'];
    }

    // Thêm vào bảng order
    $order_date = date('Y-m-d H:i:s');
    $status = 'pending';
    $sql = "INSERT INTO `order` (user_id, orderdate, total_money, payment, status) VALUES (?, ?, ?, ?, ?)";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("issss", $user_id, $order_date, $total_amount, $payment_method, $status);
    $stmt->execute();
    $order_id = $conn->insert_id;

    // Thêm chi tiết đơn hàng vào orderdetails
    $sql = "INSERT INTO orderdetails (order_id, product_id, price, count, total_money) VALUES (?, ?, ?, ?, ?)";
    $stmt = $conn->prepare($sql);
    foreach ($cart_items as $item) {
        $item_total = $item['price'] * $item['count'];
        $stmt->bind_param("iisii", $order_id, $item['product_id'], $item['price'], $item['count'], $item_total);
        $stmt->execute();

        // Cập nhật tồn kho trong product
        $sql_update = "UPDATE product SET count = count - ? WHERE product_id = ?";
        $stmt_update = $conn->prepare($sql_update);
        $stmt_update->bind_param("ii", $item['count'], $item['product_id']);
        $stmt_update->execute();
    }

    // Xóa giỏ hàng
    $sql = "DELETE FROM cart WHERE user_id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $user_id);
    $stmt->execute();

    $conn->close();
    header("Location: ../order_confirmation.php?order_id=$order_id");
    exit();
} else {
    $conn->close();
    header("Location: ../cart.php");
    exit();
}
?>