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

<body>
    <nav class="navbar navbar-expand-lg navbar-white bg-white header_index">
        <div class="container d-flex align-items-center">
            <!-- Logo và nút menu -->
            <div class="d-flex align-items-center">
                <button id="menuButton" class="btn menu-btn me-3" style="font-size: 30px;">☰</button>
                <a class="navbar-brand" href="index.php">
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


            <!-- Giỏ hàng, tài khoản, liên hệ bên phải -->
            <div class="d-flex">
                <a href="#" class="nav-link me-3 show_signin">🛒 Giỏ hàng</a>
                <a href="#" class="nav-link me-3 show_signin">👤 Tài khoản</a>
                <a href="#" class="nav-link show_signin">📞 Liên hệ</a>
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
         document.addEventListener("DOMContentLoaded", function () {
            let menuButton = document.querySelector("#menuButton");
            let sidebarMenu = document.querySelector("#sidebarMenu");
            let accountBtn = document.querySelectorAll(".show_signin");
            let loginForm = document.getElementById("loginForm");
            let closeLogin = document.getElementById("closeLogin");

            menuButton.addEventListener("mouseenter", function () {
                sidebarMenu.style.display = "block";
            });

            sidebarMenu.addEventListener("mouseleave", function () {
                sidebarMenu.style.display = "none";
            });
            accountBtn.forEach(button => {
                button.addEventListener("click", function (event) {
                    event.preventDefault();
                    loginForm.classList.add("active");
                });
            });

            closeLogin.addEventListener("click", function () {
                loginForm.classList.remove("active");
            });
        });

    </script>
</body>

</html>