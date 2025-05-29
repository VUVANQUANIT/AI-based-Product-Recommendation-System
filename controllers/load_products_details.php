<?php
require '/xampp/htdocs/WEB_LUANVAN/config/database.php';

if (!$conn) {
    die("Lỗi kết nối: " . mysqli_connect_error());
}

if (isset($_GET['product_id'])) {
    $product_id = $_GET['product_id'];


    if (!filter_var($product_id, FILTER_VALIDATE_INT)) {
        die("ID sản phẩm không hợp lệ.");
    }

  
    $sql = "SELECT product_id, product_name, price,description, image FROM product WHERE product_id = ?";
    $stmt = $conn->prepare($sql);
    
    if (!$stmt) {
        die("Lỗi SQL: " . $conn->error);
    }

    $stmt->bind_param("i", $product_id);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
    } else {
        die("Sản phẩm không tồn tại.");
    }

    $stmt->close();
} else {
    die("Thiếu tham số sản phẩm.");
}

$conn->close();
?>
