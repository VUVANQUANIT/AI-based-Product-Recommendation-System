<div id="loginForm" class="login-form">
    <div class="login-content">
        <span id="closeLogin" class="close-btn">&times;</span>
        <h3 class="text-center">Đăng Nhập</h3>
        <div id="error-message" class="alert alert-danger d-none"></div> <!-- Hiển thị lỗi -->
        <form id="loginFormData">
            <div class="mb-3">
                <label for="loginInput" class="form-label">Email hoặc Số điện thoại</label>
                <input type="text" class="form-control" id="loginInput" name="loginInput" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Mật khẩu</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100 bg-dark">Đăng nhập</button>
        </form>
        <div class="text-center mt-3">
            <span>Bạn chưa có tài khoản? <a href="/WEB_LUANVAN/signup.php" class="text-primary">Tạo tài khoản</a></span>
        </div>
    </div>
</div>


<script>
    document.getElementById("loginFormData").addEventListener("submit", function(event) {
    event.preventDefault(); 

    let formData = new FormData(this);

    fetch("./controllers/signin_backend.php", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response:", data);
        let errorMessage = document.getElementById("error-message");

        if (data.status === "error") {
            errorMessage.innerText = data.message;
            errorMessage.classList.remove("d-none");
        } else {
            window.location.href = "home.php";
        }
    })
    .catch(error => console.error("Lỗi khi gửi dữ liệu:", error));
});

</script>
