<?php
session_start();
require "/xampp/htdocs/WEB_LUANVAN/includes/header.php";

if (isset($_SESSION['user_id'])) {
    require "/xampp/htdocs/WEB_LUANVAN/includes/header_user.php";
  
}

if (!isset($_SESSION['user_id'])) {
    header("Location: signin.php"); // Chuyển hướng nếu chưa đăng nhập
    exit();
}

require "/xampp/htdocs/WEB_LUANVAN/controllers/load_cart_controller.php"; // Load giỏ hàng

if (empty($cart_items)) {
    header("Location: cart.php"); // Nếu giỏ hàng trống, quay lại trang giỏ hàng
    exit();
}
?>

<div class="checkout-container">
    <h3>💳 Thanh toán</h3>
    <div class="cart-summary">
        <h4>Sản phẩm trong giỏ hàng</h4>
        <table class="checkout-table">
            <thead>
                <tr>
                    <th>Sản phẩm</th>
                    <th>Kích cỡ</th>
                    <th>Số lượng</th>
                    <th>Giá</th>
                    <th>Tổng</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($cart_items as $item): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($item['product_name']); ?></td>
                        <td><?php echo htmlspecialchars($item['size']); ?></td>
                        <td><?php echo $item['cart_count']; ?></td>
                        <td><?php echo number_format($item['price'], 0, ',', '.') . ' đ'; ?></td>
                        <td><?php echo number_format($item['total'], 0, ',', '.') . ' đ'; ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <p>Tổng tiền: <strong><?php echo number_format($total_amount, 0, ',', '.') . ' đ'; ?></strong></p>
    </div>

    <form action="./controllers/process_checkout.php" method="POST" class="checkout-form">
        <h4>Chọn phương thức thanh toán</h4>
        <label>
            <input type="radio" name="payment_method" value="cod" checked> Thanh toán khi nhận hàng (COD)
        </label><br>
        <label>
            <input type="radio" name="payment_method" value="bank"> Chuyển khoản ngân hàng
        </label><br>
        <button type="submit" class="btn btn-checkout">Xác nhận thanh toán</button>
    </form>
</div>

<style>
    .checkout-container {
        max-width: 900px;
        margin: 60px auto;
        padding: 20px;
        background: #fff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
    }
    .checkout-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
    }
    .checkout-table th, .checkout-table td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: center;
    }
    .checkout-table th {
        background: #ff6600;
        color: white;
    }
    .checkout-form {
        margin-top: 20px;
    }
    .btn-checkout {
        background: #b2f5ea;
        color: #1d4044;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
</style>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
$(document).ready(function() {
    $('.checkout-form').on('submit', function(event) {
        event.preventDefault(); // Ngăn form submit ngay lập tức

        const cartItems = <?php echo json_encode($cart_items); ?>;

        // Gửi từng sản phẩm trong giỏ hàng đến track_behavior.php
        cartItems.forEach(item => {
            const productId = item.product_id;
            const quantity = item.cart_count;

            fetch("./controllers/track_behavior.php", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: "action_type=purchase&product_id=" + productId + "&quantity=" + quantity
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error("Lỗi gửi purchase:", error));
        });

        // Sau khi gửi xong, submit form
        this.submit();
    });
});
</script>

<?php
require "/xampp/htdocs/WEB_LUANVAN/includes/footer.php";
?>