<div id="signup" style="margin-top: 154px;">
    <div class="container mt-3 d-flex align-items-end justify-content-center">
        <form id="signup-form" class="col-md-6" method="POST" action="signup.php">
            <h1 class="text-center text-uppercase h2 mb-4">Đăng ký tài khoản</h1>

            <div id="error-message" class="alert alert-danger d-none"></div>
            <div class="row mb-4">
                <div class="col">
                    <input type="email" class="form-control w-75" name="email" placeholder="Email" required>
                </div>
            </div>
            <div class="row g-3 mb-4">
                <div class="col">
                    <input type="password" class="form-control" name="pass" placeholder="Mật khẩu" required>
                </div>
                <div class="col">
                    <input type="password" class="form-control" name="passconfirm" placeholder="Nhập lại mật khẩu" required>
                </div>
            </div>
            <div class="row g-3 mb-4">
                <div class="col">
                    <input type="text" class="form-control" name="name" placeholder="Tên" required>
                </div>
                <div class="col">
                    <input type="text" class="form-control" name="lastname" placeholder="Họ" required>
                </div>
            </div>
            <div class="row mb-4">
                <div class="col">
                    <input type="tel" class="form-control w-75" name="phone" placeholder="Số điện thoại" required pattern="[0-9]{10,11}" title="Số điện thoại phải chứa 10-11 chữ số">
                </div>
            </div>
            <div class="row mb-3">
                <div class="col">
                    <input type="text" class="form-control" name="address" placeholder="Địa chỉ" required>
                </div>
            </div>

            <div class="form-check mb-4">
                <input type="checkbox" class="form-check-input " name="agree">
                <label class="form-check-label ">Tôi đồng ý Điều kiện - Điều khoản & Chính sách bảo mật</label>
            </div>
            <div class="row mb-5">
                <button type="submit" class="btn btn-primary w-100 bg-dark text-white text-center py-3">Đăng ký</button>
            </div>
        </form>
    </div>
</div>

<script>
    document.getElementById("signup-form").addEventListener("submit", function(event) {
    event.preventDefault(); 

    let formData = new FormData(this);
    let errorMessage = document.getElementById("error-message");

    if (!document.querySelector("input[name='agree']").checked) {
        errorMessage.innerText = "Bạn cần đồng ý với Điều kiện - Điều khoản.";
        errorMessage.classList.remove("d-none");
        return;
    }
    

    fetch("./controllers/signup_backend.php", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error("Lỗi kết nối server!");
        return response.json();
    })
    .then(data => {
        console.log("Gửi dữ liệu:", [...formData.entries()]);
        console.log("Response:", data);

        if (data.status === "error") {
            errorMessage.innerText = data.message;
            errorMessage.classList.remove("d-none");
        } else {
            window.location.href = "home.php"; // Chuyển hướng khi đăng ký thành công
        }
    })
    .catch(error => {
        console.error("Lỗi khi gửi dữ liệu:", error);
        errorMessage.innerText = "Có lỗi xảy ra, vui lòng thử lại!";
        errorMessage.classList.remove("d-none");
    });
});


</script>