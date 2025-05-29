<?php
session_start();
require "/xampp/htdocs/WEB_LUANVAN/includes/header.php";

if (isset($_SESSION['user_id'])) {
    require "/xampp/htdocs/WEB_LUANVAN/includes/header_user.php";
  
}
require "/xampp/htdocs/WEB_LUANVAN/config/database.php"; // Đổi thành database.php

if (!isset($_SESSION['user_id']) || !isset($_GET['order_id'])) {
    $conn->close();
    header("Location: cart.php");
    exit();
}

$user_id = $_SESSION['user_id'];
$order_id = $_GET['order_id'];

// Load thông tin đơn hàng
$sql = "SELECT * FROM `order` WHERE order_id = ? AND user_id = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("ii", $order_id, $user_id);
$stmt->execute();
$order = $stmt->get_result()->fetch_assoc();

if (!$order) {
    $conn->close();
    header("Location: cart.php");
    exit();
}

// Load chi tiết đơn hàng
$sql = "SELECT od.*, p.product_name 
        FROM orderdetails od 
        JOIN product p ON od.product_id = p.product_id 
        WHERE od.order_id = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $order_id);
$stmt->execute();
$order_details = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);

$conn->close(); // Đóng kết nối
?>

<!-- Phần HTML/CSS giữ nguyên như trước -->
<div class="confirmation-container">
    <h3>✅ Đặt hàng thành công!</h3>
    <p>Mã đơn hàng: <strong>#<?php echo $order['order_id']; ?></strong></p>
    <p>Ngày đặt hàng: <?php echo $order['orderdate']; ?></p>
    <p>Phương thức thanh toán: <?php echo $order['payment'] === 'cod' ? 'Thanh toán khi nhận hàng' : 'Chuyển khoản ngân hàng'; ?></p>
    <h4>Chi tiết đơn hàng</h4>
    <table class="order-table">
        <thead>
            <tr>
                <th>Sản phẩm</th>
                <th>Số lượng</th>
                <th>Giá</th>
                <th>Tổng</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($order_details as $item): ?>
                <tr>
                    <td><?php echo htmlspecialchars($item['product_name']); ?></td>
                    <td><?php echo $item['count']; ?></td>
                    <td><?php echo number_format($item['price'], 0, ',', '.') . ' đ'; ?></td>
                    <td><?php echo number_format($item['total_money'], 0, ',', '.') . ' đ'; ?></td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
    <p>Tổng tiền: <strong><?php echo number_format($order['total_money'], 0, ',', '.') . ' đ'; ?></strong></p>
    <a href="home.php" class="btn btn-home">🏠 Về trang chủ</a>
</div>

<style>
    .confirmation-container {
        max-width: 900px;
        margin: 60px auto;
        padding: 20px;
        background: #fff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
    }
    .order-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
    }
    .order-table th, .order-table td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: center;
    }
    .order-table th {
        background: #ff6600;
        color: white;
    }
    .btn-home {
        background: #b2f5ea;
        color: #1d4044;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        display: inline-block;
        margin-top: 10px;
    }
</style>

<?php
require "/xampp/htdocs/WEB_LUANVAN/includes/footer.php";
?>