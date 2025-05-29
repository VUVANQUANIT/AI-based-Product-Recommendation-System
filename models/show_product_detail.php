<?php 
require "/xampp/htdocs/WEB_LUANVAN/controllers/load_products_details.php"; 

// Kiểm tra sản phẩm có tồn tại không
if (!isset($row) || empty($row)) {
    die("<div class='container text-center'><h3 class='text-danger'>Sản phẩm không tồn tại!</h3></div>");
}
?>

<div class="container" style="margin-top: 154px; margin-bottom: 200px;">
    <div class="row">
        <div class="col-md-6">
            <img src="./assets/images/Image/<?php echo !empty($row['image']) ? htmlspecialchars($row['image']) : 'default.png'; ?>" 
                 class="img-fluid rounded" alt="Sản phẩm">
        </div>

        <div class="col-md-6">
            <h2 class="product-title"><?php echo htmlspecialchars($row['product_name']); ?></h2>
            <p class="product-price text-danger fs-4 fw-bold"><?php echo number_format($row['price'], 0, ',', '.'); ?> đ</p>
            <p class="product-description" style="font-size: 18px;font-weight:400;"><?php echo nl2br(htmlspecialchars($row['description'])); ?></p>

            <form action="/controllers/add_to_cart.php" method="POST">
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
                
                <button type="submit" class="btn btn-dark w-100 show_signin" id="addToCartBtn">🛒 Thêm vào giỏ hàng</button>
            </form>
        </div>
    </div>
</div>
