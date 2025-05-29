<?php
require '/xampp/htdocs/WEB_LUANVAN/config/database.php';
session_start();

header('Content-Type: application/json');

if (!isset($_SESSION['user_name'])) {
    echo json_encode(["error" => "Người dùng chưa đăng nhập"]);
    exit;
}

$user_name = $_SESSION['user_name'];

// Lấy user_id từ bảng users dựa trên fullname
$sql_user = "SELECT user_id FROM users WHERE fullname = ?";
$stmt_user = $conn->prepare($sql_user);
if (!$stmt_user) {
    echo json_encode(["error" => "Lỗi chuẩn bị truy vấn user: " . $conn->error]);
    exit;
}
$stmt_user->bind_param("s", $user_name);
$stmt_user->execute();
$result_user = $stmt_user->get_result();

if ($result_user->num_rows === 0) {
    echo json_encode(["error" => "Không tìm thấy user_id"]);
    exit;
}

$user_data = $result_user->fetch_assoc();
$user_id = $user_data['user_id']; // Sửa lại để dùng user_id từ DB

$action_type = $_POST['action_type'] ?? null;
$product_id = isset($_POST['product_id']) ? intval($_POST['product_id']) : null;
$quantity = isset($_POST['quantity']) ? intval($_POST['quantity']) : 1;
$keyword = $_POST['keyword'] ?? null;
$key_category = isset($_POST['key_category']) ? intval($_POST['key_category']) : null;

$points = [
    'click' => 2,
    'search' => 1,
    'add_to_cart' => 5,
    'purchase' => 10,
    'remove_from_cart' => -15,
    'decrease_quantity' => -3
];

// Hàm gửi yêu cầu đến Flask API
function sendToFlask($user_id, $product_id, $action_type, $score) {
    $url = 'http://127.0.0.1:5000/update_policy';
    $data = [
        'user_id' => $user_id,
        'product_id' => $product_id,
        'action_type' => $action_type,
        'reward' => $score
    ];
    $options = [
        'http' => [
            'header'  => "Content-Type: application/json\r\n",
            'method'  => 'POST',
            'content' => json_encode($data),
        ],
    ];
    $context  = stream_context_create($options);
    $result = @file_get_contents($url, false, $context);
    if ($result === FALSE) {
        error_log("Lỗi khi gửi yêu cầu đến Flask: " . print_r($http_response_header, true));
    }
}

// Xử lý hành vi tìm kiếm (search)
if ($action_type === "search") {
    if (!empty($key_category)) {
        $search_sql = "SELECT product_id FROM product WHERE category_id = ?";
        $stmt_search = $conn->prepare($search_sql);
        if (!$stmt_search) {
            echo json_encode(["error" => "Lỗi chuẩn bị truy vấn search: " . $conn->error]);
            exit;
        }
        $stmt_search->bind_param("i", $key_category);
    } elseif (!empty($keyword)) {
        $search_sql = "SELECT product_id FROM product WHERE product_name LIKE ?";
        $stmt_search = $conn->prepare($search_sql);
        if (!$stmt_search) {
            echo json_encode(["error" => "Lỗi chuẩn bị truy vấn search: " . $conn->error]);
            exit;
        }
        $search_param = "%" . $keyword . "%";
        $stmt_search->bind_param("s", $search_param);
    } else {
        echo json_encode(["error" => "Thiếu từ khóa tìm kiếm hoặc category_id"]);
        exit;
    }

    $stmt_search->execute();
    $result_search = $stmt_search->get_result();
    $updated_products = 0;

    while ($row = $result_search->fetch_assoc()) {
        $product_id = $row['product_id'];

        $check_sql = "SELECT score FROM user_behavior WHERE user_id = ? AND product_id = ? AND action_type = ?";
        $stmt = $conn->prepare($check_sql);
        if (!$stmt) {
            echo json_encode(["error" => "Lỗi chuẩn bị truy vấn check: " . $conn->error]);
            exit;
        }
        $stmt->bind_param("iis", $user_id, $product_id, $action_type);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $new_score = $row['score'] + $points['search'];

            $update_sql = "UPDATE user_behavior SET score = ?, timestamp = NOW() WHERE user_id = ? AND product_id = ? AND action_type = ?";
            $update_stmt = $conn->prepare($update_sql);
            if (!$update_stmt) {
                echo json_encode(["error" => "Lỗi chuẩn bị cập nhật: " . $conn->error]);
                exit;
            }
            $update_stmt->bind_param("iiis", $new_score, $user_id, $product_id, $action_type);
            $update_stmt->execute();
            $update_stmt->close();
        } else {
            $insert_sql = "INSERT INTO user_behavior (user_id, product_id, action_type, score, timestamp) VALUES (?, ?, ?, ?, NOW())";
            $insert_stmt = $conn->prepare($insert_sql);
            if (!$insert_stmt) {
                echo json_encode(["error" => "Lỗi chuẩn bị chèn: " . $conn->error]);
                exit;
            }
            $insert_stmt->bind_param("iisi", $user_id, $product_id, $action_type, $points['search']);
            $insert_stmt->execute();
            $insert_stmt->close();
        }
        sendToFlask($user_id, $product_id, $action_type, $points['search']); // Gửi đến Flask
        $updated_products++;
    }

    $stmt_search->close();
    echo json_encode(["success" => "Cập nhật điểm tìm kiếm cho $updated_products sản phẩm"]);
    $conn->close();
    exit;
}

// Xử lý các hành động khác (click, add_to_cart, purchase, remove_from_cart, decrease_quantity)
if (!$action_type || !$product_id || !isset($points[$action_type])) {
    echo json_encode(["error" => "Thiếu dữ liệu hoặc action_type không hợp lệ"]);
    exit;
}

$score = $points[$action_type];

// Điều chỉnh điểm số dựa trên quantity
if (in_array($action_type, ['add_to_cart', 'purchase', 'decrease_quantity', 'remove_from_cart'])) {
    $score *= $quantity;
}

// Kiểm tra xem đã có dữ liệu user_behavior chưa
$check_sql = "SELECT score FROM user_behavior WHERE user_id = ? AND product_id = ? AND action_type = ?";
$stmt = $conn->prepare($check_sql);
if (!$stmt) {
    echo json_encode(["error" => "Lỗi chuẩn bị truy vấn check: " . $conn->error]);
    exit;
}
$stmt->bind_param("iis", $user_id, $product_id, $action_type);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows > 0) {
    $row = $result->fetch_assoc();
    $new_score = $row['score'] + $score;

    $update_sql = "UPDATE user_behavior SET score = ?, timestamp = NOW() WHERE user_id = ? AND product_id = ? AND action_type = ?";
    $update_stmt = $conn->prepare($update_sql);
    if (!$update_stmt) {
        echo json_encode(["error" => "Lỗi chuẩn bị cập nhật: " . $conn->error]);
        exit;
    }
    $update_stmt->bind_param("iiis", $new_score, $user_id, $product_id, $action_type);
    if ($update_stmt->execute()) {
        sendToFlask($user_id, $product_id, $action_type, $score); // Gửi đến Flask
        echo json_encode([
            "success" => "Điểm đã được cập nhật",
            "new_score" => $new_score,
            "quantity" => $quantity
        ]);
    } else {
        echo json_encode(["error" => "Lỗi khi cập nhật điểm: " . $conn->error]);
    }
    $update_stmt->close();
} else {
    $insert_sql = "INSERT INTO user_behavior (user_id, product_id, action_type, score, timestamp) VALUES (?, ?, ?, ?, NOW())";
    $insert_stmt = $conn->prepare($insert_sql);
    if (!$insert_stmt) {
        echo json_encode(["error" => "Lỗi chuẩn bị chèn: " . $conn->error]);
        exit;
    }
    $insert_stmt->bind_param("iisi", $user_id, $product_id, $action_type, $score);
    if ($insert_stmt->execute()) {
        sendToFlask($user_id, $product_id, $action_type, $score); // Gửi đến Flask
        echo json_encode([
            "success" => "Đã ghi nhận hành vi mới",
            "score" => $score,
            "quantity" => $quantity
        ]);
    } else {
        echo json_encode(["error" => "Lỗi khi ghi nhận hành vi: " . $conn->error]);
    }
    $insert_stmt->close();
}

$stmt->close();
$conn->close();
?>