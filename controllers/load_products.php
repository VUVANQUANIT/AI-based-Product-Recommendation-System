<?php
session_start();
require '/xampp/htdocs/WEB_LUANVAN/config/database.php';

// Kiểm tra kết nối database
if ($conn->connect_error) {
    die(json_encode(["error" => "Database connection failed: " . $conn->connect_error]));
}

$user_id = $_SESSION['user_id'] ?? null;
$page = (int)($_GET['page'] ?? 1);
$limit = 18;
$start = ($page - 1) * $limit;

$category_id = $_GET['category_id'] ?? '';
$search = $_GET['search'] ?? '';

// Hàm trả về JSON và thoát
function sendResponse($data) {
    global $conn;
    echo json_encode($data);
    $conn->close();
    exit;
}

// Xử lý tìm kiếm hoặc lọc theo danh mục
if ($search || $category_id) {
    $total_sql = "SELECT COUNT(*) AS total FROM product WHERE 1=1";
    $sql = "SELECT * FROM product WHERE 1=1";
    $params = [];
    $types = '';

    if ($category_id) {
        $total_sql .= " AND category_id = ?";
        $sql .= " AND category_id = ?";
        $params[] = $category_id;
        $types .= 's';
    }
    if ($search) {
        $total_sql .= " AND product_name LIKE ?";
        $sql .= " AND product_name LIKE ?";
        $params[] = "%$search%";
        $types .= 's';
    }

    $stmt = $conn->prepare($total_sql);
    if ($params) $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $total_products = $stmt->get_result()->fetch_assoc()['total'];
    $total_pages = ceil($total_products / $limit);

    $sql .= " LIMIT ?, ?";
    $stmt = $conn->prepare($sql);
    $params[] = $start;
    $params[] = $limit;
    $types .= 'ii';
    $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $result = $stmt->get_result();

    $products = [];
    while ($row = $result->fetch_assoc()) {
        $products[] = $row;
    }

    sendResponse(["products" => $products, "total_pages" => $total_pages]);
}

// Nếu chưa đăng nhập: Hiển thị sản phẩm mặc định
if (!$user_id) {
    $total_sql = "SELECT COUNT(*) AS total FROM product WHERE 1=1";
    $sql = "SELECT * FROM product WHERE 1=1";
    $params = [];
    $types = '';

    if ($category_id) {
        $total_sql .= " AND category_id = ?";
        $sql .= " AND category_id = ?";
        $params[] = $category_id;
        $types .= 's';
    }

    $stmt = $conn->prepare($total_sql);
    if ($params) $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $total_products = $stmt->get_result()->fetch_assoc()['total'];
    $total_pages = ceil($total_products / $limit);

    $sql .= " LIMIT ?, ?";
    $stmt = $conn->prepare($sql);
    $params[] = $start;
    $params[] = $limit;
    $types .= 'ii';
    $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $result = $stmt->get_result();

    $products = [];
    while ($row = $result->fetch_assoc()) {
        $products[] = $row;
    }

    sendResponse(["products" => $products, "total_pages" => $total_pages]);
}

// Nếu đã đăng nhập: Lấy sản phẩm gợi ý từ API và hiển thị hết trước
$recommended_products = [];
$recommended_ids = [];

$recommend_api_url = "http://localhost:5000/recommend?user_id=" . urlencode($user_id);
$response = @file_get_contents($recommend_api_url);
if ($response === false) {
    error_log("Failed to fetch recommendations for user $user_id");
} else {
    $recommend_data = json_decode($response, true);
    if (!empty($recommend_data['recommendations'])) {
        $recommended_ids = array_map('intval', $recommend_data['recommendations']);
        $recommended_ids_string = implode(',', $recommended_ids);

        $sql = "SELECT * FROM product WHERE product_id IN ($recommended_ids_string) ORDER BY FIELD(product_id, $recommended_ids_string)";
        $result = $conn->query($sql);
        while ($row = $result->fetch_assoc()) {
            $recommended_products[] = $row;
        }
    }
}

// Tính tổng số sản phẩm và trang
$total_recommended = count($recommended_products);
$total_sql = "SELECT COUNT(*) AS total FROM product WHERE product_id NOT IN (" . ($recommended_ids ? implode(',', $recommended_ids) : '0') . ")";
$params = [];
$types = '';

if ($category_id) {
    $total_sql .= " AND category_id = ?";
    $params[] = $category_id;
    $types .= 's';
}

$stmt = $conn->prepare($total_sql);
if ($params) $stmt->bind_param($types, ...$params);
$stmt->execute();
$total_default = $stmt->get_result()->fetch_assoc()['total'];
$total_products = $total_recommended + $total_default;
$total_pages = ceil($total_products / $limit);

// Xử lý phân trang
$final_products = [];

if ($start < $total_recommended) {
    // Lấy sản phẩm gợi ý nếu $start nằm trong phạm vi gợi ý
    $recommended_slice = array_slice($recommended_products, $start, $limit);
    $final_products = $recommended_slice;
}

// Tính số lượng còn thiếu và lấy sản phẩm mặc định nếu cần
$remaining_slots = $limit - count($final_products);
if ($remaining_slots > 0) {
    $default_start = max(0, $start - $total_recommended);
    $sql = "SELECT * FROM product WHERE product_id NOT IN (" . ($recommended_ids ? implode(',', $recommended_ids) : '0') . ")";
    if ($category_id) {
        $sql .= " AND category_id = ?";
        $params = [$category_id];
        $types = 's';
    }
    $sql .= " LIMIT ?, ?";
    $params[] = $default_start;
    $params[] = $remaining_slots;
    $types .= 'ii';

    $stmt = $conn->prepare($sql);
    $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $result = $stmt->get_result();

    while ($row = $result->fetch_assoc()) {
        $final_products[] = $row;
    }
}

sendResponse(["products" => $final_products, "total_pages" => $total_pages]);
?>