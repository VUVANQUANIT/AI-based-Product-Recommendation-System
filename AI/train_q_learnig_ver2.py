from flask import Flask, request, jsonify
import numpy as np
import mysql.connector
import logging
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kết nối MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="thoitrang"
)
cursor = conn.cursor()

# Khởi tạo Q-table
Q_table = defaultdict(lambda: defaultdict(float))
alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.3  # Exploration rate ban đầu
epsilon_min = 0.01  # Giá trị epsilon tối thiểu
epsilon_decay = 0.995  # Hệ số giảm epsilon

# Lấy danh sách tất cả product_id
cursor.execute("SELECT product_id FROM product")
all_products = [row[0] for row in cursor.fetchall()]

# Lấy trạng thái hiện tại của user (dựa trên hành vi gần đây)
def get_current_state(user_id):
    query = """
        SELECT p.category_id 
        FROM user_behavior ub
        JOIN product p ON ub.product_id = p.product_id
        WHERE ub.user_id = %s 
        AND ub.timestamp > %s
        ORDER BY ub.timestamp DESC 
        LIMIT 1
    """
    cursor.execute(query, (user_id, datetime.now() - timedelta(hours=24)))
    result = cursor.fetchone()
    category_id = result[0] if result else 0
    return f"{user_id}_{category_id}"

# Lưu Q-value vào MySQL
def save_q_value(state, product_id, q_value):
    cursor.execute(
        "INSERT INTO q_table (user_id, product_id, q_value) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE q_value = %s",
        (int(state.split('_')[0]), product_id, q_value, q_value)
    )
    conn.commit()

# Tải Q-table từ MySQL
def load_q_table():
    global Q_table
    cursor.execute("SELECT user_id, product_id, q_value FROM q_table")
    for user_id, product_id, q_value in cursor.fetchall():
        state = get_current_state(user_id)
        Q_table[state][product_id] = q_value
    logging.info("Q-table loaded from MySQL")

# Huấn luyện ban đầu từ user_behavior
def train_initial_q_table():
    cursor.execute("""
        SELECT ub.user_id, ub.product_id, ub.score, p.category_id
        FROM user_behavior ub
        JOIN product p ON ub.product_id = p.product_id
    """)
    for user_id, product_id, score, category_id in cursor.fetchall():
        state = f"{user_id}_{category_id}"
        current_q = Q_table[state][product_id]
        new_q = current_q + alpha * (score - current_q)
        Q_table[state][product_id] = new_q
        save_q_value(state, product_id, new_q)
    logging.info("Initial Q-table training completed")

# Tải và huấn luyện khi khởi động
load_q_table()
train_initial_q_table()

# API cập nhật Q-table
@app.route('/update_policy', methods=['POST'])
def update_policy():
    global epsilon
    data = request.get_json()
    user_id = data['user_id']
    product_id = data['product_id']
    action_type = data['action_type']
    reward = data['reward']

    state = get_current_state(user_id)
    current_q = Q_table[state][product_id]
    next_state = get_current_state(user_id)
    next_max_q = max(Q_table[next_state].values(), default=0)
    new_q = current_q + alpha * (reward + gamma * next_max_q - current_q)
    Q_table[state][product_id] = new_q
    save_q_value(state, product_id, new_q)

    epsilon = max(epsilon_min, epsilon * epsilon_decay)
    logging.info(f"Updated Q-value for state {state}, product {product_id}: {new_q}")
    return jsonify({"success": "Q-table updated", "epsilon": epsilon})

# API trả về gợi ý (hỗ trợ GET và POST, tùy chọn trả tất cả sản phẩm)
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({"error": "Thiếu user_id trong JSON"}), 400
        user_id = data['user_id']
        page = data.get('page', 1)
        limit = data.get('limit', 18)
        return_all = data.get('all', False)
    else:  # GET
        user_id = request.args.get('user_id')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 18))
        return_all = request.args.get('all', 'false').lower() == 'true'
        if not user_id:
            return jsonify({"error": "Thiếu user_id trong query string"}), 400
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({"error": "user_id phải là số nguyên"}), 400

    state = get_current_state(user_id)

    # Nếu yêu cầu trả tất cả sản phẩm
    if return_all:
        # Lấy tất cả sản phẩm, sắp xếp theo Q-value
        product_scores = Q_table[state]
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = [p[0] for p in sorted_products]
        # Bổ sung các sản phẩm chưa có Q-value
        remaining = set(all_products) - set(recommendations)
        recommendations.extend(list(remaining))

        logging.info(f"✅ Trả tất cả sản phẩm cho user {user_id}, state {state}: {len(recommendations)} sản phẩm")
        return jsonify({"recommendations": recommendations})

    # Logic phân trang thông thường
    start = (page - 1) * limit
    if np.random.rand() < epsilon:
        # Khám phá: Chọn ngẫu nhiên đủ sản phẩm cho 2 trang (36)
        total_needed = limit * 2
        recommendations = np.random.choice(all_products, min(total_needed, len(all_products)), replace=False).tolist()
    else:
        # Khai thác: Chọn sản phẩm có Q-value cao nhất
        product_scores = Q_table[state]
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = [p[0] for p in sorted_products]
        if len(recommendations) < limit * 2:
            remaining = set(all_products) - set(recommendations)
            recommendations.extend(np.random.choice(list(remaining), min(limit * 2 - len(recommendations), len(remaining)), replace=False))

    recommendations_page = recommendations[start:start + limit]

    logging.info(f"✅ Gợi ý cho user {user_id}, state {state}, page {page}: {recommendations_page}")
    return jsonify({"recommendations": recommendations_page})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)#backup