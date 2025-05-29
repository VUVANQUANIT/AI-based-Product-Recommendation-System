<?php
session_start();

require_once "../config/database.php"; // Đường dẫn tương đối từ controllers/

if (!$conn) {
    die(json_encode(['success' => false, 'message' => 'Lỗi kết nối database']));
}

header('Content-Type: application/json');

if (!isset($_SESSION['user_id'])) {
    echo json_encode(['success' => false, 'message' => 'Bạn cần đăng nhập để thực hiện thao tác này']);
    exit;
}

$user_id = $_SESSION['user_id'];
$action = $_POST['action'] ?? '';
$cart_id = (int)($_POST['cart_id'] ?? 0);

$response = ['success' => false];

if ($cart_id > 0) {
    switch ($action) {
        case 'update_quantity':
            $change = (int)$_POST['change'];

            // Lấy thông tin hiện tại
            $sql = "SELECT c.`count`, c.product_id, p.price 
                    FROM cart c 
                    JOIN product p ON c.product_id = p.product_id 
                    WHERE c.cart_id = ? AND c.user_id = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("ii", $cart_id, $user_id);
            $stmt->execute();
            $result = $stmt->get_result();
            $item = $result->fetch_assoc();

            if (!$item) {
                $response['message'] = "Không tìm thấy sản phẩm trong giỏ hàng";
                break;
            }

            $current_count = $item['count'];
            $new_count = $current_count + $change;
            if ($new_count < 1) $new_count = 1;

            // Cập nhật số lượng
            $sql = "UPDATE cart SET `count` = ? WHERE cart_id = ? AND user_id = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("iii", $new_count, $cart_id, $user_id);
            if (!$stmt->execute()) {
                $response['message'] = "Lỗi khi cập nhật số lượng: " . $conn->error;
                break;
            }

            $total = $new_count * $item['price'];

            // Tính tổng tiền giỏ hàng
            $sql = "SELECT SUM(c.`count` * p.price) as total_amount 
                    FROM cart c 
                    JOIN product p ON c.product_id = p.product_id 
                    WHERE c.user_id = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("i", $user_id);
            $stmt->execute();
            $result = $stmt->get_result();
            $total_amount = $result->fetch_assoc()['total_amount'] ?? 0;

            $response = [
                'success' => true,
                'new_count' => $new_count,
                'total' => number_format($total, 0, ',', '.') . ' đ',
                'total_amount' => number_format($total_amount, 0, ',', '.') . ' đ',
                'product_id' => $item['product_id'] // Thêm product_id
            ];
            break;

        case 'delete_item':
            // Lấy product_id trước khi xóa
            $sql = "SELECT product_id FROM cart WHERE cart_id = ? AND user_id = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("ii", $cart_id, $user_id);
            $stmt->execute();
            $result = $stmt->get_result();
            $item = $result->fetch_assoc();

            if (!$item) {
                $response['message'] = "Không tìm thấy sản phẩm trong giỏ hàng";
                break;
            }

            // Xóa sản phẩm
            $sql = "DELETE FROM cart WHERE cart_id = ? AND user_id = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("ii", $cart_id, $user_id);
            if (!$stmt->execute()) {
                $response['message'] = "Lỗi khi xóa sản phẩm: " . $conn->error;
                break;
            }

            // Tính lại tổng tiền
            $sql = "SELECT SUM(c.`count` * p.price) as total_amount 
                    FROM cart c 
                    JOIN product p ON c.product_id = p.product_id 
                    WHERE c.user_id = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("i", $user_id);
            $stmt->execute();
            $result = $stmt->get_result();
            $total_amount = $result->fetch_assoc()['total_amount'] ?? 0;

            $response = [
                'success' => true,
                'total_amount' => number_format($total_amount, 0, ',', '.') . ' đ',
                'product_id' => $item['product_id'] // Thêm product_id
            ];
            break;

        default:
            $response['message'] = "Hành động không hợp lệ";
            break;
    }
} else {
    $response['message'] = "ID giỏ hàng không hợp lệ";
}

$conn->close();
echo json_encode($response);
?>