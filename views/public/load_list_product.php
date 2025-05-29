<div class="container my-5">
        <h2 class="text-center">Sản Phẩm Nổi Bật</h2>
        <div class="row" id="product-list">
        <?php require "./ajax/get_products.php"; ?>  
        </div>
</div>
<nav aria-label="Page navigation" class="mt-4">
    <ul class="pagination justify-content-center" id="pagination">
    </ul>
</nav>