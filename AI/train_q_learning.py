import json
import pymysql
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kết nối MySQL
def get_data():
    try:
        conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, product_id, action_type, score FROM user_behavior ORDER BY user_id, timestamp")
        data = cursor.fetchall()
        conn.close()
        logging.info("✅ Đã lấy dữ liệu từ MySQL")
        return data
    except pymysql.Error as e:
        logging.error(f"Lỗi kết nối MySQL: {e}")
        return []

# Huấn luyện Q-Learning
def train_q_learning(data, alpha=0.1, gamma=0.9, episodes=100):
    if not data:
        logging.error("Không có dữ liệu để huấn luyện")
        return {}, {}

    # Ánh xạ user_id và product_id
    user_dict, product_dict = {}, {}
    for user_id, product_id, _, _ in data:
        if user_id not in user_dict:
            user_dict[user_id] = len(user_dict)
        if product_id not in product_dict:
            product_dict[product_id] = len(product_dict)

    state_dim = len(user_dict) + len(product_dict)
    Q_table = {}

    # Chuẩn bị dữ liệu
    user_history = {}
    for user_id, product_id, _, reward in data:
        if user_id not in user_history:
            user_history[user_id] = []

        state = np.zeros(state_dim)
        state[user_dict[user_id]] = 1
        if user_history[user_id]:
            state[len(user_dict) + product_dict[user_history[user_id][-1]]] = 1
        state_key = tuple(state)

        if state_key not in Q_table:
            Q_table[state_key] = {}

        action = product_dict[product_id]
        if action not in Q_table[state_key]:
            Q_table[state_key][action] = 0

        next_state = np.zeros(state_dim)
        next_state[user_dict[user_id]] = 1
        next_state[len(user_dict) + product_dict[product_id]] = 1
        next_state_key = tuple(next_state)

        if next_state_key not in Q_table:
            Q_table[next_state_key] = {}

        old_q = Q_table[state_key][action]
        future_q = max(Q_table[next_state_key].values(), default=0)
        Q_table[state_key][action] = (1 - alpha) * old_q + alpha * (reward + gamma * future_q)

        user_history[user_id].append(product_id)

    # Lưu Q-table và dicts
    with open("q_table.json", "w") as f:
        json.dump({str(k): v for k, v in Q_table.items()}, f, indent=4)
    np.save("user_dict.npy", user_dict)
    np.save("product_dict.npy", product_dict)
    return user_dict, product_dict

# Huấn luyện
logging.info("🔄 Đang huấn luyện Q-Learning...")
data = get_data()
user_dict, product_dict = train_q_learning(data)
logging.info("✅ Đã hoàn tất huấn luyện Q-Learning!")

# Flask API
app = Flask(__name__)
CORS(app)

@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        user_dict = np.load("user_dict.npy", allow_pickle=True).item()
        product_dict = np.load("product_dict.npy", allow_pickle=True).item()
        with open("q_table.json", "r") as f:
            Q_table = {tuple(map(float, k.strip("()").split(","))): v for k, v in json.load(f).items()}

        user_id = request.args.get('user_id')
        user_id = int(user_id) if user_id and user_id.isdigit() else user_id

        if user_id not in user_dict:
            logging.info(f"Không có dữ liệu cho user_id: {user_id}")
            return jsonify({"user_id": user_id, "recommendations": []})

        # Lấy lịch sử gần nhất
        conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')
        cursor = conn.cursor()
        cursor.execute("SELECT product_id FROM user_behavior WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1", (user_id,))
        last_product = cursor.fetchone()
        conn.close()

        # Tạo state
        state = np.zeros(len(user_dict) + len(product_dict))
        state[user_dict[user_id]] = 1
        if last_product:
            state[len(user_dict) + product_dict[last_product[0]]] = 1
        state_key = tuple(state)

        # Lấy tất cả sản phẩm, bổ sung Q=0 cho sản phẩm chưa có
        recommendations = Q_table.get(state_key, {})
        all_products = {int(k): float(v) for k, v in recommendations.items()}
        for action in range(len(product_dict)):
            if action not in all_products:
                all_products[action] = 0.0

        sorted_recommendations = sorted(all_products.items(), key=lambda x: x[1], reverse=True)
        product_array = np.array(list(product_dict.keys()))
        recommended_products = [int(product_array[int(action)]) for action, _ in sorted_recommendations]

        # In danh sách product_id gợi ý theo định dạng log
        logging.info(f"✅ Gợi ý cho user {user_id}: {recommended_products}")

        return jsonify({"user_id": user_id, "recommendations": recommended_products})
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)