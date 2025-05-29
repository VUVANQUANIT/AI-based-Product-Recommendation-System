<?php
session_start();

require "/xampp/htdocs/WEB_LUANVAN/includes/header.php";

if (isset($_SESSION['user_id'])) {
    require "/xampp/htdocs/WEB_LUANVAN/includes/header_user.php";
}
$isLoggedIn = isset($_SESSION['user_id']);
require "./views/user/signin_form.php";
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Thời Trang Nữ</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">
    <link rel="stylesheet" href="./assets/css/style.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<style>
    .custom-alert {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        min-width: 300px;
        max-width: 90%;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        background-color: rgba(255, 255, 255, 0.95);
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
        z-index: 1050;
    }

    .custom-alert.show {
        opacity: 1;
    }

    .custom-alert-success {
        border: 2px solid #28a745;
        color: #155724;
    }

    .custom-alert-danger {
        border: 2px solid #dc3545;
        color: #721c24;
    }

    .alert-icon {
        margin-right: 15px;
        font-size: 24px;
    }

    .alert-content {
        flex-grow: 1;
        font-size: 16px;
        line-height: 1.4;
    }

    .alert-close {
        margin-left: 15px;
        font-size: 24px;
        cursor: pointer;
        color: inherit;
        opacity: 0.7;
    }

    .alert-close:hover {
        opacity: 1;
    }
</style>

<body>


    <!-- Sidebar Menu -->
    <div id="sidebarMenu" class="sidebar-menu">
        <ul>
            <li><a href="#" class="category-link" data-category-id="">Tất cả</a></li>
            <li><a href="#" class="category-link" data-category-id="1">Đầm</a></li>
            <li><a href="#" class="category-link" data-category-id="2">Áo</a></li>
            <li><a href="#" class="category-link" data-category-id="3">Chân váy</a></li>
            <li><a href="#" class="category-link" data-category-id="4">Quần</a></li>
            <li><a href="#" class="category-link" data-category-id="5">Giày/dép</a></li>
            <li><a href="#" class="category-link" data-category-id="6">Túi</a></li>
        </ul>
    </div>


    <?php require "/xampp/htdocs/WEB_LUANVAN/controllers/load_products_details.php"; ?>

    <?php if (!isset($row) || empty($row)): ?>
        <div class="container text-center">
            <h3 class="text-danger">Sản phẩm không tồn tại!</h3>
        </div>
    <?php else: ?>
        <div class="container mt-5 mb-5">
            <div class="row" style="margin-top:120px;">
                <div class="col-md-6">
                    <img src="./assets/images/Image/<?php echo !empty($row['image']) ? htmlspecialchars($row['image']) : 'default.png'; ?>"
                        class="img-fluid rounded" alt="Sản phẩm">
                </div>
                <div class="col-md-6">
                    <h2 class="product-title"><?php echo htmlspecialchars($row['product_name']); ?></h2>
                    <p class="product-price text-danger fs-4 fw-bold"><?php echo number_format($row['price'], 0, ',', '.'); ?> đ</p>
                    <p class="product-description"><?php echo nl2br(htmlspecialchars($row['description'])); ?></p>


                    <form id="addToCartForm"
                        <?php echo $isLoggedIn ? 'action="/controllers/add_to_cart_controller.php"' : ''; ?>
                        method="POST"
                        class="<?php echo $isLoggedIn ? '' : 'show_signin'; ?>">
                        <input type="hidden" name="product_id" value="<?php echo htmlspecialchars($row['product_id']); ?>">
                        <div class="mb-3">
                            <label for="quantity" class="form-label">Số lượng:</label>
                            <input type="number" id="quantity" name="quantity" class="form-control" value="1" min="1" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Kích cỡ:</label>
                            <div>
                                <input type="radio" id="sizeS" name="size" value="S" required> <label for="sizeS">S</label>
                                <input type="radio" id="sizeM" name="size" value="M" class="ms-3" required> <label for="sizeM">M</label>
                                <input type="radio" id="sizeL" name="size" value="L" class="ms-3" required> <label for="sizeL">L</label>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-dark w-100 <?php echo  $product_id ?>" id="addToCartBtn">🛒 Thêm vào giỏ hàng</button>
                    </form>
                </div>
            </div>
        </div>
    <?php endif; ?>

    <div id="loginForm" class="login-form">
        <div class="login-content">
            <span id="closeLogin" class="close-btn">&times;</span>
            <h3 class="text-center">Đăng Nhập</h3>
            <form action="process_login.php" method="POST">
                <div class="mb-3">
                    <label class="form-label">Email hoặc Số điện thoại</label>
                    <input type="text" class="form-control" name="loginInput" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Mật khẩu</label>
                    <input type="password" class="form-control" name="password" required>
                </div>
                <button type="submit" class="btn btn-dark w-100">Đăng nhập</button>
                <p class="text-center mt-3">
                    Chưa có tài khoản? <a href="signup.php">Tạo tài khoản</a>
                </p>
            </form>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const isLoggedIn = <?php echo json_encode($isLoggedIn); ?>;
            const loginForm = document.getElementById("loginForm");
            const addToCartForm = document.getElementById("addToCartForm");
            const addToCartBtn = document.getElementById("addToCartBtn");
            const quantity_product = document.getElementById("quantity");

            // Xử lý khi nhấn nút "Thêm vào giỏ hàng"
            addToCartBtn.addEventListener("click", function(event) {
                if (!isLoggedIn) {
                    event.preventDefault();
                    loginForm.classList.add("active");
                }
            });

            // Đóng form đăng nhập
            document.getElementById("closeLogin").addEventListener("click", function() {
                loginForm.classList.remove("active");
            });

            // Xử lý gửi form thêm vào giỏ hàng
            if (addToCartForm) {
                addToCartForm.addEventListener("submit", function(event) {
                    event.preventDefault();
                    const quantity = parseInt(document.getElementById("quantity").value);
                    const size = document.querySelector('input[name="size"]:checked');

                    if (quantity < 1 || !size) {
                        showErrorMessage("Vui lòng chọn số lượng và kích cỡ hợp lệ!");
                        return;
                    }

                    const formData = new FormData(addToCartForm);
                    fetch("./controllers/add_to_cart_controller.php", { // Giữ đường dẫn gốc
                            method: "POST",
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === "success") {
                                const productName = "<?php echo htmlspecialchars($row['product_name']); ?>";
                                showSuccessMessage(`Đã thêm <strong>${quantity} ${productName} (kích cỡ ${size.value})</strong> vào giỏ hàng!`);
                            } else {
                                showErrorMessage(data.message);
                            }
                        })
                        .catch(error => showErrorMessage("Lỗi: " + error.message));
                    fetch("./controllers/track_behavior.php", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/x-www-form-urlencoded"
                            },
                            body: `action_type=add_to_cart&product_id=${<?php echo htmlspecialchars($product_id); ?>}&quantity=${quantity}`
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log("Track behavior response:", data);
                        })
                        .catch(error => {
                            console.error("Lỗi khi gửi dữ liệu đến track_behavior.php:", error);
                        });

                });

            }

            // Hàm hiển thị thông báo thành công
            function showSuccessMessage(message) {
                const successMessage = document.createElement("div");
                successMessage.className = "custom-alert custom-alert-success";
                successMessage.innerHTML = `
                <div class="alert-icon"><i class="fas fa-check-circle"></i></div>
                <div class="alert-content">${message}</div>
                <span class="alert-close">×</span>
            `;
                document.body.appendChild(successMessage);
                setTimeout(() => successMessage.classList.add("show"), 10); // Fade-in
                setTimeout(() => {
                    successMessage.classList.remove("show");
                    setTimeout(() => successMessage.remove(), 300); // Fade-out
                }, 3000);

                successMessage.querySelector(".alert-close").addEventListener("click", () => {
                    successMessage.classList.remove("show");
                    setTimeout(() => successMessage.remove(), 300);
                });
            }

            // Hàm hiển thị thông báo lỗi
            function showErrorMessage(message) {
                const errorMessage = document.createElement("div");
                errorMessage.className = "custom-alert custom-alert-danger";
                errorMessage.innerHTML = `
                <div class="alert-icon"><i class="fas fa-exclamation-circle"></i></div>
                <div class="alert-content">${message}</div>
                <span class="alert-close">×</span>
            `;
                document.body.appendChild(errorMessage);
                setTimeout(() => errorMessage.classList.add("show"), 10); // Fade-in
                setTimeout(() => {
                    errorMessage.classList.remove("show");
                    setTimeout(() => errorMessage.remove(), 300); // Fade-out
                }, 3000);

                errorMessage.querySelector(".alert-close").addEventListener("click", () => {
                    errorMessage.classList.remove("show");
                    setTimeout(() => errorMessage.remove(), 300);
                });
            }
        });
    </script>


</body>

</html>
<?php
require "/xampp/htdocs/WEB_LUANVAN/includes/footer.php";
?>