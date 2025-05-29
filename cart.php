<?php
session_start();
require "/xampp/htdocs/WEB_LUANVAN/includes/header.php";

if (isset($_SESSION['user_id'])) {
    require "/xampp/htdocs/WEB_LUANVAN/includes/header_user.php";
    require "/xampp/htdocs/WEB_LUANVAN/controllers/load_cart_controller.php";
}
$isLoggedIn = isset($_SESSION['user_id']);
require "./views/user/signin_form.php";
?>

<div class="cart-container">
    <h3>🛒 Giỏ hàng của bạn</h3>
    <?php if (empty($cart_items)): ?>
        <p>Giỏ hàng của bạn đang trống.</p>
    <?php else: ?>
        <table class="cart-table">
            <thead>
                <tr>
                    <th>Hình ảnh</th>
                    <th>Sản phẩm</th>
                    <th>Kích cỡ</th>
                    <th>Số lượng</th>
                    <th>Giá</th>
                    <th>Tổng</th>
                    <th>Hành động</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($cart_items as $item): ?>
                    <tr data-cart-id="<?php echo $item['cart_id']; ?>">
                        <td><img src="./assets/images/Image/<?php echo htmlspecialchars($item['image']); ?>" alt="<?php echo htmlspecialchars($item['product_name']); ?>"></td>
                        <td><?php echo htmlspecialchars($item['product_name']); ?></td>
                        <td><?php echo htmlspecialchars($item['size']); ?></td>
                        <td>
                            <div class="quantity-controls">
                                <button class="btn btn-minus" onclick="updateQuantity(<?php echo $item['cart_id']; ?>, -1)">➖</button>
                                <span id="qty-<?php echo $item['cart_id']; ?>"><?php echo $item['cart_count']; ?></span>
                                <button class="btn btn-plus" onclick="updateQuantity(<?php echo $item['cart_id']; ?>, 1)">➕</button>
                            </div>
                        </td>
                        <td><?php echo number_format($item['price'], 0, ',', '.') . ' đ'; ?></td>
                        <td id="total-<?php echo $item['cart_id']; ?>"><?php echo number_format($item['total'], 0, ',', '.') . ' đ'; ?></td>
                        <td>
                            <button class="btn btn-delete" onclick="showDeleteModal(<?php echo $item['cart_id']; ?>, '<?php echo htmlspecialchars($item['product_name']); ?>')">Xoá</button>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <p class="cart-summary">🛍️ Tổng tiền: <span id="total-price"><?php echo number_format($total_amount, 0, ',', '.') . ' đ'; ?></span></p>
        <a href="checkout.php" class="btn btn-checkout">💳 Thanh toán</a>
    <?php endif; ?>
</div>

<!-- Modal xác nhận xóa -->
<div id="deleteModal" class="modal">
    <div class="modal-content">
        <h4>Xác nhận xóa sản phẩm</h4>
        <p>Bạn có chắc muốn xóa <strong id="modal-product-name"></strong> khỏi giỏ hàng?</p>
        <div class="modal-buttons">
            <button class="btn btn-confirm" onclick="confirmDelete()">Xác nhận</button>
            <button class="btn btn-cancel" onclick="hideDeleteModal()">Hủy</button>
        </div>
    </div>
</div>

<script>
let currentCartId = null;

function updateQuantity(cartId, change) {
    fetch('./controllers/cart_actions.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `action=update_quantity&cart_id=${cartId}&change=${change}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`qty-${cartId}`).textContent = data.new_count;
            document.getElementById(`total-${cartId}`).textContent = data.total;
            document.getElementById('total-price').textContent = data.total_amount;

            // Gửi hành vi decrease_quantity nếu giảm số lượng
            if (change < 0) {
                fetch('./controllers/track_behavior.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action_type=decrease_quantity&product_id=${data.product_id}&quantity=1`
                })
                .then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error('Lỗi gửi decrease_quantity:', error));
            }
        } else {
            alert(data.message || 'Có lỗi xảy ra');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại.');
    });
}

function showDeleteModal(cartId, productName) {
    currentCartId = cartId; 
    document.getElementById('modal-product-name').textContent = productName;
    document.getElementById('deleteModal').style.display = 'block';
}

function hideDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    currentCartId = null; 
}

function confirmDelete() {
    if (currentCartId) {
        fetch('./controllers/cart_actions.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `action=delete_item&cart_id=${currentCartId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`tr[data-cart-id="${currentCartId}"]`).remove();
                document.getElementById('total-price').textContent = data.total_amount;
                if (!document.querySelector('.cart-table tbody tr')) {
                    document.querySelector('.cart-table').style.display = 'none';
                    document.querySelector('.cart-container').innerHTML += '<p>Giỏ hàng của bạn đang trống.</p>';
                }

                // Gửi hành vi remove_from_cart
                fetch('./controllers/track_behavior.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action_type=remove_from_cart&product_id=${data.product_id}&quantity=1`
                })
                .then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error('Lỗi gửi remove_from_cart:', error));

                hideDeleteModal(); 
            } else {
                alert(data.message || 'Có lỗi xảy ra');
                hideDeleteModal();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại.');
            hideDeleteModal();
        });
    }
}

// Đóng modal khi nhấp ra ngoài
window.onclick = function(event) {
    const modal = document.getElementById('deleteModal');
    if (event.target === modal) {
        hideDeleteModal();
    }
}
</script>

<style>
    .cart-container {
        max-width: 900px;
        margin: 20px auto;
        margin-bottom: 450px;
        padding: 20px;
        background: #fff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
    }
    .cart-container h3 {
        text-align: center;
    }
    .cart-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .cart-table th, .cart-table td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: center;
    }
    .cart-table th {
        background: #ff6600;
        color: white;
    }
    .cart-table th:nth-child(5),
    .cart-table td:nth-child(5) {
        min-width: 120px;
        padding: 10px 15px;
    }
    .cart-table th:nth-child(6),
    .cart-table td:nth-child(6) {
        min-width: 150px;
        padding: 10px 15px;
    }
    .cart-table td img {
        max-width: 50px;
        border-radius: 5px;
    }
    .quantity-controls {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 5px;
    }
    .btn {
        padding: 6px 10px;
        border: none;
        cursor: pointer;
        border-radius: 5px;
    }
    .btn-minus, .btn-plus {
        background: #a3bffa;
        color: #1a2b5f;
    }
    .btn-delete {
        background: #feb2b2;
        color: #7f1d1d;
        padding: 8px 12px;
    }
    .btn-checkout {
        background: #b2f5ea;
        color: #1d4044;
        padding: 10px 15px;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
        float: right;
    }
    .cart-summary {
        margin-top: 10px;
        text-align: right;
    }
    .cart-container::after {
        content: "";
        display: table;
        clear: both;
    }

    /* CSS cho modal */
    .modal {
        display: none;
        position: fixed;
        z-index: 1;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
    }
    .modal-content {
        background-color: #fff;
        margin: 15% auto;
        padding: 20px;
        border-radius: 8px;
        width: 80%;
        max-width: 400px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        text-align: center;
    }
    .modal-content h4 {
        margin: 0 0 15px;
        color: #333;
    }
    .modal-content p {
        margin: 0 0 20px;
        color: #666;
    }
    .modal-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    .btn-confirm {
        background: #ff4d4d;
        color: white;
        padding: 8px 16px;
    }
    .btn-confirm:hover {
        background: #e60000;
    }
    .btn-cancel {
        background: #ccc;
        color: #333;
        padding: 8px 16px;
    }
    .btn-cancel:hover {
        background: #b3b3b3;
    }
</style>

<?php
require "/xampp/htdocs/WEB_LUANVAN/includes/footer.php";
?>