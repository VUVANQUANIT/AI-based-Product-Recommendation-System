<div id="product-list" class="row"></div>
<div id="pagination" class="text-center mt-4"></div> 

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
    $(document).ready(function() {
        let currentPage = 1;
        let selectedCategory = '';
        let currentSearch = '';
        $("#product-list").html("<p>Đang tải sản phẩm...</p>"); 

        function loadProducts(page) {
            $.ajax({
                url: "./controllers/load_products.php",
                type: "GET",
                data: {
                    page: page,
                    category_id: selectedCategory,
                    search: currentSearch
                },
                dataType: "json",
                success: function(response) {
                    let html = "";
                    response.products.forEach(product => {
                        html += `
                        <div class="col-md-4">
                            <div class="card product-card">
                                <a href="product_detail.php?product_id=${product.product_id}" class="product-link" data-product-id="${product.product_id}">
                                    <img src="./assets/images/Image/${product.image}" alt="Sản phẩm">
                                </a>
                                <div class="card-body text-center">
                                    <h5 class="card-title">
                                        <a href="product_detail.php?product_id=${product.product_id}" class="product-link" data-product-id="${product.product_id}" style="text-decoration: none;color: black;">${product.product_name}</a>
                                    </h5>
                                    <p class="card-text text-danger">${parseInt(product.price).toLocaleString("vi-VN")}đ</p>
                                    
                                </div>
                            </div>
                        </div>`;
                    });
                    $("#product-list").html(html);
                    generatePagination(response.total_pages);
                },
                error: function(xhr, status, error) {
                    console.error("Lỗi AJAX:", xhr.responseText);
                    $("#product-list").html("<p class='text-danger'>Lỗi tải sản phẩm: " + xhr.responseText + "</p>");
                }

            });
        }


        $(document).on("click", ".product-link", function(event) {
            event.preventDefault();
            let productId = $(this).data("product-id");

            fetch("./controllers/track_behavior.php", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: "action_type=click&product_id=" + productId
            });


            window.location.href = "product_detail.php?product_id=" + productId;
        });

        function generatePagination(totalPages) {
            let paginationHTML = "";
            for (let i = 1; i <= totalPages; i++) {
                paginationHTML += `<button class="btn btn-outline-primary mx-1 ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
            }
            $("#pagination").html(paginationHTML);
        }

        window.changePage = function(page) {
            currentPage = page;
            loadProducts(page);
        }


        $(document).on("click", ".buy-now", function(event) {
            event.preventDefault();
            let loginForm = $("#loginForm");
            if (loginForm.length) {
                loginForm.addClass("active");
            } else {
                console.warn("Không tìm thấy #loginForm");
            }
        });


        $(document).on("click", ".category-link", function() {
            selectedCategory = $(this).data("category-id");
            currentSearch = '';

            fetch("./controllers/track_behavior.php", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: "action_type=search&key_category=" + encodeURIComponent(selectedCategory)
                })
                .then(response => response.json())
                .then(data => console.log(data));

            loadProducts(1);
        });

        $("#search-btn").click(function(event) {
            event.preventDefault();
            selectedCategory = '';
            currentSearch = $("#search-input").val();

            if (currentSearch.trim() !== "") {
                fetch("./controllers/track_behavior.php", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded"
                        },
                        body: "action_type=search&keyword=" + encodeURIComponent(currentSearch)
                    }).then(response => response.json())
                    .then(data => console.log(data));
            }
            loadProducts(1);
        });

        loadProducts(currentPage);
    });
</script>