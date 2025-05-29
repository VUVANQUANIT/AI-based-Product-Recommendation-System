<?php
session_start();
header("Content-Type: application/json");
ini_set('display_errors', 1);
error_reporting(E_ALL);
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "thoitrang";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die(json_encode(["status" => "error", "message" => "Kết nối thất bại: " . $conn->connect_error]));
}


if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(["status" => "error", "message" => "Yêu cầu không hợp lệ!"]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $email = $_POST['email'];
    $pass = $_POST['pass'];
    $passconfirm = $_POST['passconfirm'];
    $name = $_POST['name'];
    $lastname = $_POST['lastname'];
    $phone = $_POST['phone'];
    $address = $_POST['address'];

    $error = [];
    $success = "";

    if ($pass !== $passconfirm) {

        echo json_encode(["status" => "error", "message" => "Mật khẩu không khớp!"]);
        exit;
    }

    if (!isset($_POST['agree'])) {

        echo json_encode(["status" => "error", "message" => "Bạn cần đồng ý với điều khoản và chính sách bảo mật."]);
        exit;
    }

    $role = isset($_POST['role']) ? $_POST['role'] : 'customer';    
    $fullname = $name . ' ' . $lastname;

    $stmt_email = mysqli_prepare($conn, "SELECT * FROM users WHERE email = ?");
    mysqli_stmt_bind_param($stmt_email, "s", $email);
    mysqli_stmt_execute($stmt_email);
    $result_email = mysqli_stmt_get_result($stmt_email);

    if (mysqli_num_rows($result_email) > 0) {

        echo json_encode(["status" => "error", "message" => "Email đã được sử dụng!"]);
        exit;
    }
    mysqli_stmt_close($stmt_email);


    $stmt_phone = mysqli_prepare($conn, "SELECT * FROM users WHERE phone = ?");
    mysqli_stmt_bind_param($stmt_phone, "s", $phone);
    mysqli_stmt_execute($stmt_phone);
    $result_phone = mysqli_stmt_get_result($stmt_phone);

    if (mysqli_num_rows($result_phone) > 0) {

        echo json_encode(["status" => "error", "message" => "Số điện thoại đã được sử dụng!"]);
        exit;
    }
    mysqli_stmt_close($stmt_phone);

    if (empty($error)) {
        // Chèn dữ liệu vào bảng users
        $query = "INSERT INTO users (fullname, email, role, pass, address, phone) VALUES (?,?,?,?,?,?)";
        $stmt = mysqli_prepare($conn, $query);
        mysqli_stmt_bind_param($stmt, "ssssss", $fullname, $email, $role, $pass, $address, $phone);

        if (mysqli_stmt_execute($stmt)) {
        
            $user_id = mysqli_insert_id($conn);
            $_SESSION['user_id'] = $user_id;
            $_SESSION['user_name'] = $fullname;
            $_SESSION['user_email'] = $email;
            echo json_encode(["status" => "OK", "message" => "Đăng nhập thành công!"]);
        } else {
           
            echo json_encode(["status" => "error", "message" => "Lỗi khi đăng ký: " . mysqli_error($conn)]);

        }

        mysqli_stmt_close($stmt);
        $conn->close();
    }
}
