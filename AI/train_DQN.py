import numpy as np
import pymysql
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from collections import deque
import random

# Thiết lập logging
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
        logging.error(f"❌ Lỗi kết nối MySQL: {e}")
        return []

# Mô hình DQN
class DQNModel:
    def __init__(self, state_dim, action_dim):
        self.model = keras.Sequential([
            layers.Dense(64, activation="relu", input_shape=(state_dim,)),
            layers.Dense(64, activation="relu"),
            layers.Dense(action_dim, activation="linear")
        ])
        self.model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), 
                          loss=keras.losses.MeanSquaredError())
        self.target_model = keras.models.clone_model(self.model)
        self.target_model.set_weights(self.model.get_weights())

    def predict(self, states):
        return self.model.predict(states, verbose=0)

    def train(self, states, targets, batch_size=32):
        self.model.fit(states, targets, batch_size=batch_size, epochs=1, verbose=0)

    def update_target(self):
        self.target_model.set_weights(self.model.get_weights())

    def save(self, filename="dqn_model.keras"):
        self.model.save(filename)
        logging.info(f"✅ Đã lưu mô hình vào {filename}")

    def load(self, filename="dqn_model.keras"):
        self.model = keras.models.load_model(filename)
        self.target_model = keras.models.clone_model(self.model)
        self.target_model.set_weights(self.model.get_weights())
        logging.info(f"✅ Đã load mô hình từ {filename}")

# Huấn luyện DQN với Experience Replay
def train_dqn(data, episodes=10, gamma=0.9, batch_size=32, replay_size=1000):
    if not data:
        logging.error("❌ Không có dữ liệu để huấn luyện")
        return {}, {}

    user_dict, product_dict = {}, {}
    for user_id, product_id, _, _ in data:
        if user_id not in user_dict:
            user_dict[user_id] = len(user_dict)
        if product_id not in product_dict:
            product_dict[product_id] = len(product_dict)

    num_users, num_products = len(user_dict), len(product_dict)
    state_dim = num_users + num_products  # Trạng thái gồm user_id và sản phẩm trước đó
    model = DQNModel(state_dim, num_products)

    replay_buffer = deque(maxlen=replay_size)
    epsilon = 1.0

    # Chuẩn bị dữ liệu dạng (state, action, reward, next_state)
    user_history = {}
    for i, (user_id, product_id, _, reward) in enumerate(data):
        if user_id not in user_history:
            user_history[user_id] = []
        state = np.zeros(state_dim)
        if user_history[user_id]:
            state[user_dict[user_id]] = 1
            state[num_users + product_dict[user_history[user_id][-1]]] = 1
        else:
            state[user_dict[user_id]] = 1
        next_state = np.zeros(state_dim)
        next_state[user_dict[user_id]] = 1
        next_state[num_users + product_dict[product_id]] = 1
        replay_buffer.append((state, product_dict[product_id], reward, next_state))
        user_history[user_id].append(product_id)

    # Huấn luyện
    for episode in range(episodes):
        logging.info(f"🔄 Episode {episode + 1}/{episodes}")
        if len(replay_buffer) >= batch_size:
            batch = random.sample(replay_buffer, batch_size)
            states = np.array([x[0] for x in batch])
            actions = [x[1] for x in batch]
            rewards = [x[2] for x in batch]
            next_states = np.array([x[3] for x in batch])

            q_targets = model.predict(states)
            q_next = model.target_model.predict(next_states)
            for i in range(batch_size):
                q_targets[i, actions[i]] = rewards[i] + gamma * np.max(q_next[i])
            model.train(states, q_targets, batch_size)
            model.update_target()
        epsilon = max(0.1, epsilon * 0.99)

    model.save()
    np.save("user_dict.npy", user_dict)
    np.save("product_dict.npy", product_dict)
    return user_dict, product_dict

# Huấn luyện
logging.info("🔄 Đang huấn luyện DQN...")
data = get_data()
user_dict, product_dict = train_dqn(data, episodes=10, batch_size=32)
logging.info("✅ Đã hoàn tất huấn luyện DQN!")

# API Flask
app = Flask(__name__)
CORS(app)

@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        if not os.path.exists("dqn_model.keras"):
            return jsonify({"error": "Mô hình chưa được huấn luyện"}), 500

        user_dict = np.load("user_dict.npy", allow_pickle=True).item()
        product_dict = np.load("product_dict.npy", allow_pickle=True).item()
        user_id = request.args.get('user_id')
        user_id = int(user_id) if user_id and user_id.isdigit() else user_id

        if user_id not in user_dict:
            logging.warning(f"⚠️ User {user_id} không tồn tại trong dữ liệu huấn luyện")
            return jsonify({"user_id": user_id, "recommendations": []})

        model = DQNModel(len(user_dict) + len(product_dict), len(product_dict))
        model.load()

        # Lấy lịch sử gần nhất của người dùng
        conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')
        cursor = conn.cursor()
        cursor.execute("SELECT product_id FROM user_behavior WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1", (user_id,))
        last_product = cursor.fetchone()
        conn.close()

        state = np.zeros(len(user_dict) + len(product_dict))
        state[user_dict[user_id]] = 1
        if last_product:
            state[len(user_dict) + product_dict[last_product[0]]] = 1

        q_values = model.predict(np.array([state]))[0]
        product_array = np.array(list(product_dict.keys()))
        recommended_products = product_array[np.argsort(q_values)[::-1]].tolist()

        logging.info(f"✅ Gợi ý cho user {user_id}: {recommended_products}")
        return jsonify({"user_id": user_id, "recommendations": recommended_products})

    except Exception as e:
        logging.error(f"❌ Lỗi: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)