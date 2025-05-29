import numpy as np
import pymysql
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from collections import deque
import random
import os
import threading
import time
from datetime import datetime
import json

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kết nối MySQL toàn cục
conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')

def get_data():
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ub.user_id, ub.product_id, ub.action_type, ub.score, p.category_id, ub.timestamp
            FROM user_behavior ub
            JOIN product p ON ub.product_id = p.product_id
            ORDER BY ub.user_id, ub.timestamp
        """)
        data = cursor.fetchall()
        logging.info("✅ Đã lấy dữ liệu từ MySQL")
        return data
    except pymysql.Error as e:
        logging.error(f"❌ Lỗi kết nối MySQL: {e}")
        return []

class PolicyGradientModel:
    def __init__(self, state_dim, action_dim):
        self.model = keras.Sequential([
            layers.Input(shape=(state_dim,)),
            layers.Dense(128, activation="relu"),
            layers.Dense(128, activation="relu"),
            layers.Dense(action_dim, activation="softmax")
        ])
        self.optimizer = keras.optimizers.Adam(learning_rate=0.001)
        self.action_dim = action_dim
        self.state_dim = state_dim

    def predict(self, state):
        return self.model.predict(np.array([state]), verbose=0)[0]

    def train(self, states, actions, rewards):
        with tf.GradientTape() as tape:
            probs = self.model(states, training=True)
            action_masks = tf.one_hot(actions, self.action_dim)
            selected_probs = tf.reduce_sum(probs * action_masks, axis=1)
            loss = -tf.reduce_mean(tf.math.log(selected_probs + 1e-10) * rewards)
        grads = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

    def save(self, filename="policy_model.keras"):
        self.model.save(filename)
        with open("model_config.json", "w") as f:
            json.dump({"state_dim": self.state_dim, "action_dim": self.action_dim}, f)
        logging.info(f"✅ Đã lưu mô hình vào {filename}")

    def load(self, filename="policy_model.keras"):
        self.model = keras.models.load_model(filename)
        with open("model_config.json", "r") as f:
            config = json.load(f)
            self.state_dim = config["state_dim"]
            self.action_dim = config["action_dim"]
        logging.info(f"✅ Đã load mô hình từ {filename}")

# Dữ liệu toàn cục
global_data = {
    "user_dict": {},
    "product_dict": {},
    "category_dict": {},
    "state_dim": 0,
    "action_dim": 0,
    "last_updated": 0
}

def update_global_data():
    data = get_data()
    global_data["user_dict"] = {uid: idx for idx, uid in enumerate(sorted(set(d[0] for d in data)))}
    global_data["product_dict"] = {pid: idx for idx, pid in enumerate(sorted(set(d[1] for d in data)))}
    global_data["category_dict"] = {cid: idx for idx, cid in enumerate(sorted(set(d[4] for d in data)))}
    global_data["state_dim"] = len(global_data["user_dict"]) + 5 * len(global_data["product_dict"]) + len(global_data["category_dict"]) + 1
    global_data["action_dim"] = len(global_data["product_dict"])
    global_data["last_updated"] = time.time()
    logging.info(f"Đã cập nhật dữ liệu toàn cục: state_dim={global_data['state_dim']}, action_dim={global_data['action_dim']}")

def train_policy_gradient(model, data, episodes=20, history_length=5):
    if not data:
        logging.error("❌ Không có dữ liệu để huấn luyện")
        return

    user_history = {}
    replay_buffer = deque(maxlen=2000)

    for user_id, product_id, action_type, reward, category_id, timestamp in data:
        if user_id not in user_history:
            user_history[user_id] = []
        state = np.zeros(global_data["state_dim"])
        state[global_data["user_dict"][user_id]] = 1
        for i, prod in enumerate(user_history[user_id][-history_length:]):
            if prod in global_data["product_dict"]:
                state[len(global_data["user_dict"]) + i * global_data["action_dim"] + global_data["product_dict"][prod]] = 1
        if category_id in global_data["category_dict"]:
            state[len(global_data["user_dict"]) + 5 * global_data["action_dim"] + global_data["category_dict"][category_id]] = 1
        state[-1] = (datetime.now() - timestamp).total_seconds() / 86400
        action = global_data["product_dict"][product_id]
        replay_buffer.append((state, action, reward))
        user_history[user_id].append(product_id)

    for episode in range(episodes):
        if len(replay_buffer) >= 64:
            batch = random.sample(replay_buffer, 64)
            states = np.array([x[0] for x in batch])
            actions = np.array([x[1] for x in batch])
            rewards = np.array([x[2] for x in batch])
            model.train(states, actions, rewards)
        logging.info(f"🔄 Episode {episode + 1}/{episodes}")

    model.save()

# Khởi tạo mô hình toàn cục
update_global_data()
model = PolicyGradientModel(global_data["state_dim"], global_data["action_dim"])
if os.path.exists("policy_model.keras"):
    try:
        model.load()
        if model.state_dim != global_data["state_dim"] or model.action_dim != global_data["action_dim"]:
            logging.warning(f"Kích thước không khớp: mô hình cũ ({model.state_dim}, {model.action_dim}) vs hiện tại ({global_data['state_dim']}, {global_data['action_dim']}). Huấn luyện lại.")
            model = PolicyGradientModel(global_data["state_dim"], global_data["action_dim"])
            data = get_data()
            train_policy_gradient(model, data, episodes=5)
    except Exception as e:
        logging.error(f"Lỗi khi tải mô hình: {e}. Khởi tạo mô hình mới.")
        model = PolicyGradientModel(global_data["state_dim"], global_data["action_dim"])
else:
    logging.info("🔄 Đang huấn luyện Policy Gradient...")
    data = get_data()
    train_policy_gradient(model, data, episodes=20)

def background_training():
    global model
    while True:
        time.sleep(300)
        update_global_data()
        if model.state_dim != global_data["state_dim"] or model.action_dim != global_data["action_dim"]:
            logging.info("Kích thước thay đổi, khởi tạo lại mô hình")
            model = PolicyGradientModel(global_data["state_dim"], global_data["action_dim"])
            data = get_data()
            train_policy_gradient(model, data, episodes=5)
        else:
            data = get_data()
            train_policy_gradient(model, data, episodes=1)
        logging.info("Đã huấn luyện mô hình trong background")

threading.Thread(target=background_training, daemon=True).start()

app = Flask(__name__)
CORS(app)

def get_recommendations(user_id, top_k=40):
    global model
    if not model or user_id not in global_data["user_dict"]:
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, SUM(score) as total_score FROM user_behavior GROUP BY product_id ORDER BY total_score DESC LIMIT %s", (top_k,))
        popular = [row[0] for row in cursor.fetchall()]
        return popular if popular else random.sample(list(global_data["product_dict"].keys()), min(top_k, len(global_data["product_dict"])))

    cursor = conn.cursor()
    cursor.execute("""
        SELECT ub.product_id, ub.score, ub.timestamp, p.category_id 
        FROM user_behavior ub 
        JOIN product p ON ub.product_id = p.product_id 
        WHERE ub.user_id = %s 
        ORDER BY ub.timestamp DESC LIMIT 5
    """, (user_id,))
    history = cursor.fetchall()

    cursor.execute("SELECT product_id FROM user_behavior WHERE user_id = %s AND action_type = 'remove_from_cart'", (user_id,))
    ignored = {row[0] for row in cursor.fetchall()}

    state = np.zeros(global_data["state_dim"])
    state[global_data["user_dict"][user_id]] = 1
    for i, (prod, score, ts, cat) in enumerate(history):
        if prod in global_data["product_dict"]:
            state[len(global_data["user_dict"]) + i * global_data["action_dim"] + global_data["product_dict"][prod]] = score
        if cat in global_data["category_dict"]:
            state[len(global_data["user_dict"]) + 5 * global_data["action_dim"] + global_data["category_dict"][cat]] = 1
        state[-1] = (datetime.now() - ts).total_seconds() / 86400

    if state.shape[0] != model.state_dim:
        logging.error(f"Kích thước state không khớp: {state.shape[0]} vs {model.state_dim}. Khởi tạo lại mô hình.")
        model = PolicyGradientModel(global_data["state_dim"], global_data["action_dim"])
        data = get_data()
        train_policy_gradient(model, data, episodes=5)

    probs = model.predict(state)
    product_array = list(global_data["product_dict"].keys())  # Chuyển thành list Python ngay từ đầu
    scores = [(pid, prob + (0.1 if pid in [h[0] for h in history] else 0)) for pid, prob in zip(product_array, probs)]
    scores.sort(key=lambda x: x[1], reverse=True)
    recommendations = [int(pid) for pid, _ in scores if pid not in ignored][:top_k]  # Chuyển thành int Python

    if random.random() < 0.2:
        random_product = random.choice(list(global_data["product_dict"].keys()))
        if random_product not in recommendations and random_product not in ignored:
            recommendations.append(int(random_product))  # Chuyển thành int Python

    return recommendations

@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        user_id = int(request.args.get('user_id', 0))
        recommendations = get_recommendations(user_id)
        logging.info(f" Gợi ý cho user {user_id}: {recommendations}")
        return jsonify({"user_id": user_id, "recommendations": recommendations})
    except Exception as e:
        logging.error(f" Lỗi: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/update_policy', methods=['POST'])
def update_policy():
    global model
    try:
        data = request.json
        user_id = int(data.get("user_id"))
        product_id = data.get("product_id")
        action_type = data.get("action_type")
        reward = float(data.get("reward"))

        if not all([user_id in global_data["user_dict"], product_id in global_data["product_dict"], reward is not None]):
            return jsonify({"error": "Dữ liệu không hợp lệ"}), 400

        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_behavior (user_id, product_id, action_type, score, timestamp) VALUES (%s, %s, %s, %s, NOW())",
                       (user_id, product_id, action_type, reward))
        conn.commit()

        # Sửa truy vấn để tránh lỗi ambiguous
        cursor.execute("""
            SELECT ub.product_id, ub.score, ub.timestamp, p.category_id 
            FROM user_behavior ub 
            JOIN product p ON ub.product_id = p.product_id 
            WHERE ub.user_id = %s 
            ORDER BY ub.timestamp DESC LIMIT 5
        """, (user_id,))
        history = cursor.fetchall()

        state = np.zeros(global_data["state_dim"])
        state[global_data["user_dict"][user_id]] = 1
        for i, (prod, score, ts, cat) in enumerate(history):
            if prod in global_data["product_dict"]:
                state[len(global_data["user_dict"]) + i * global_data["action_dim"] + global_data["product_dict"][prod]] = score
            if cat in global_data["category_dict"]:
                state[len(global_data["user_dict"]) + 5 * global_data["action_dim"] + global_data["category_dict"][cat]] = 1
            state[-1] = (datetime.now() - ts).total_seconds() / 86400

        action = global_data["product_dict"][product_id]
        model.train(np.array([state]), np.array([action]), np.array([reward]))
        model.save()

        recommendations = get_recommendations(user_id)
        logging.info(f"📦 Gợi ý mới cho user {user_id} sau hành động '{action_type}' trên {product_id}: {recommendations}")
        return jsonify({
            "message": "Policy updated",
            "user_id": user_id,
            "product_id": product_id,
            "action_type": action_type,
            "recommendations": recommendations
        })
    except Exception as e:
        logging.error(f"❌ Lỗi: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        conn.close()