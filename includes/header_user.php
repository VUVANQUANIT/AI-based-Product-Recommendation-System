<?php
session_start();
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
.dropdown:hover .dropdown-menu {
    display: block;
}
.dropdown-menu {
    display: none;
    position: absolute;
    background-color: white;
    border: 1px solid #ddd;
    min-width: 150px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}
.dropdown-menu li {
    padding: 5px 10px;
}
.dropdown-menu li a {
    text-decoration: none;
    color: black;
    display: block;
}
.dropdown-menu li a:hover {
    background-color: #f1f1f1;
}

</style>
<body>
    <nav class="navbar navbar-expand-lg navbar-white bg-white header_index">
        <div class="container d-flex align-items-center">
            <!-- Logo và nút menu -->
            <div class="d-flex align-items-center">
                <button id="menuButton" class="btn menu-btn me-3" style="font-size: 30px;">☰</button>
                <a class="navbar-brand" href="home.php">
                    <img src="./assets/images/Q (1).png" alt="Logo" style="height: 80px;">
                </a>
            </div>

            <!-- Thanh tìm kiếm ở giữa -->
            <div class="d-flex flex-grow-1 justify-content-center">
                <form id="search-form" class="d-flex w-50">
                    <input id="search-input" class="form-control me-2" type="search" placeholder="Tìm kiếm" aria-label="Search">
                    <button id="search-btn" class="btn btn-outline-dark" type="submit">🔍</button>
                </form>
            </div>


            
            <div class="d-flex align-items-center">
                <a href="cart.php" class="nav-link me-3">🛒 Giỏ hàng</a>

                <!-- Menu tài khoản -->
                <div class="dropdown">
                    <a href="#" class="nav-link me-3 dropdown-toggle" id="accountMenu" role="button">
                        👤 <span id="userName"><?php echo "Thông tin tài khoản";?></span>
                    </a>
                    <ul class="dropdown-menu" id="accountDropdown">
                        <li><a class="dropdown-item" href="account.php">Tài khoản</a></li>
                        <li><a class="dropdown-item" href="/WEB_LUANVAN/controllers/logout.php">Đăng xuất</a></li>
                    </ul>
                </div>

                <a href="#" class="nav-link">📞 Liên hệ</a>
            </div>

        </div>


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
    </nav>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            let menuButton = document.querySelector("#menuButton");
            let sidebarMenu = document.querySelector("#sidebarMenu");
            
            let loginForm = document.getElementById("loginForm");
            

            menuButton.addEventListener("mouseenter", function() {
                sidebarMenu.style.display = "block";
            });

            sidebarMenu.addEventListener("mouseleave", function() {
                sidebarMenu.style.display = "none";
            });
           

            
        });
    </script>
    <?php if (isset($_SESSION['user_name'])): ?>
    <script>
        document.getElementById("userName").textContent = "<?php echo $_SESSION['user_name']; ?>";
    </script>
<?php endif; ?>
</body>

</html>