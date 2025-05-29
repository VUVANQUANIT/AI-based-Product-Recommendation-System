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
import time

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kết nối MySQL
def get_data():
    try:
        conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, product_id, action_type, score, timestamp FROM user_behavior ORDER BY user_id, timestamp")
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
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.model = self._build_model()
        self.target_model = keras.models.clone_model(self.model)
        self.target_model.set_weights(self.model.get_weights())
        self.epsilon = 1.0  # Khởi tạo epsilon cho exploration
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.99

    def _build_model(self):
        model = keras.Sequential([
            layers.Input(shape=(self.state_dim,)),
            layers.Dense(128, activation="relu"),
            layers.Dense(128, activation="relu"),
            layers.Dense(self.action_dim, activation="linear")
        ])
        model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), 
                      loss=keras.losses.MeanSquaredError())
        return model

    def predict(self, states):
        return self.model.predict(states, verbose=0)

    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        q_values = self.predict(np.array([state]))[0]
        return np.argmax(q_values)

    def train(self, states, targets, batch_size=32):
        self.model.fit(states, targets, batch_size=batch_size, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_target(self):
        self.target_model.set_weights(self.model.get_weights())

    def save(self, filename="dqn_model.keras"):
        self.model.save(filename)
        with open("dqn_config.json", "w") as f:
            json.dump({"state_dim": self.state_dim, "action_dim": self.action_dim}, f)
        logging.info(f" Đã lưu mô hình vào {filename}")

    def load(self, filename="dqn_model.keras"):
        self.model = keras.models.load_model(filename)
        self.target_model = keras.models.clone_model(self.model)
        self.target_model.set_weights(self.model.get_weights())
        with open("dqn_config.json", "r") as f:
            config = json.load(f)
            self.state_dim = config["state_dim"]
            self.action_dim = config["action_dim"]
        logging.info(f" Đã load mô hình từ {filename}")

# Dữ liệu toàn cục
global_data = {
    "user_dict": {},
    "product_dict": {},
    "state_dim": 0,
    "action_dim": 0,
    "last_updated": 0
}

def update_global_data(data=None):
    if data is None:
        data = get_data()
    global_data["user_dict"] = {uid: idx for idx, uid in enumerate(sorted(set(d[0] for d in data)))}
    global_data["product_dict"] = {pid: idx for idx, pid in enumerate(sorted(set(d[1] for d in data)))}
    global_data["state_dim"] = len(global_data["user_dict"]) + len(global_data["product_dict"])
    global_data["action_dim"] = len(global_data["product_dict"])
    global_data["last_updated"] = time.time()
    logging.info(f"Đã cập nhật dữ liệu toàn cục: state_dim={global_data['state_dim']}, action_dim={global_data['action_dim']}")

def get_state(user_id, last_product_id=None):
    state = np.zeros(global_data["state_dim"])
    if user_id in global_data["user_dict"]:
        state[global_data["user_dict"][user_id]] = 1
    if last_product_id in global_data["product_dict"]:
        state[len(global_data["user_dict"]) + global_data["product_dict"][last_product_id]] = 1
    return state

# Huấn luyện DQN với Experience Replay
def train_dqn(model, data, episodes=10, gamma=0.9, batch_size=32, replay_size=1000):
    if not data:
        logging.error("❌ Không có dữ liệu để huấn luyện")
        return

    replay_buffer = deque(maxlen=replay_size)
    user_history = {}

    # Chuẩn bị replay buffer
    for user_id, product_id, _, reward, _ in data:
        if user_id not in user_history:
            user_history[user_id] = []
        state = get_state(user_id, user_history[user_id][-1] if user_history[user_id] else None)
        next_state = get_state(user_id, product_id)
        action = global_data["product_dict"][product_id]
        replay_buffer.append((state, action, reward, next_state))
        user_history[user_id].append(product_id)

    # Huấn luyện
    for episode in range(episodes):
        if len(replay_buffer) < batch_size:
            logging.warning(f"⚠️ Không đủ dữ liệu trong replay buffer: {len(replay_buffer)}/{batch_size}")
            continue
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
        logging.info(f"🔄 Episode {episode + 1}/{episodes}")
    
    model.save()

# Khởi tạo mô hình
update_global_data()
model = DQNModel(global_data["state_dim"], global_data["action_dim"])
if os.path.exists("dqn_model.keras") and os.path.exists("dqn_config.json"):
    with open("dqn_config.json", "r") as f:
        config = json.load(f)
        if config["state_dim"] == global_data["state_dim"] and config["action_dim"] == global_data["action_dim"]:
            model.load()
            logging.info(f"✅ Đã load mô hình với state_dim={global_data['state_dim']}")
        else:
            # Tạo mô hình tạm để load trọng số cũ
            old_model = DQNModel(config["state_dim"], config["action_dim"])
            old_model.load()
            old_weights = old_model.model.get_weights()
            new_weights = model.model.get_weights()
            # Chuyển giao trọng số tương thích
            for i in range(len(old_weights)):
                if old_weights[i].shape == new_weights[i].shape:
                    new_weights[i] = old_weights[i]
                else:
                    # Điều chỉnh trọng số cho tầng đầu tiên nếu state_dim thay đổi
                    if i == 0:  # Tầng đầu tiên (weights)
                        old_shape = old_weights[i].shape
                        new_weights[i][:old_shape[0], :old_shape[1]] = old_weights[i]
                    elif i == 1:  # Bias của tầng đầu tiên
                        new_weights[i][:old_weights[i].shape[0]] = old_weights[i]
            model.model.set_weights(new_weights)
            logging.info(f"✅ Chuyển giao trọng số từ mô hình cũ (state_dim={config['state_dim']}) sang mô hình mới (state_dim={global_data['state_dim']})")
else:
    logging.info(f"✅ Tạo mô hình mới với state_dim={global_data['state_dim']}")

# Huấn luyện ban đầu
data = get_data()
train_dqn(model, data, episodes=10)

# API Flask
app = Flask(__name__)
CORS(app)

@app.route('/recommend', methods=['GET'])
def recommend():
    global model
    try:
        if time.time() - global_data["last_updated"] > 60:  # Cập nhật mỗi 60 giây
            old_state_dim = global_data["state_dim"]
            update_global_data()
            if model.state_dim != global_data["state_dim"]:
                logging.warning(f"⚠️ state_dim thay đổi: cũ={model.state_dim}, mới={global_data['state_dim']}")
                old_model = model
                model = DQNModel(global_data["state_dim"], global_data["action_dim"])
                # Chuyển giao trọng số
                old_weights = old_model.model.get_weights()
                new_weights = model.model.get_weights()
                for i in range(len(old_weights)):
                    if old_weights[i].shape == new_weights[i].shape:
                        new_weights[i] = old_weights[i]
                    else:
                        if i == 0:
                            old_shape = old_weights[i].shape
                            new_weights[i][:old_shape[0], :old_shape[1]] = old_weights[i]
                        elif i == 1:
                            new_weights[i][:old_weights[i].shape[0]] = old_weights[i]
                model.model.set_weights(new_weights)
                logging.info("✅ Đã chuyển giao trọng số sang mô hình mới")

        user_id = request.args.get('user_id')
        user_id = int(user_id) if user_id and user_id.isdigit() else None
        if not user_id or user_id not in global_data["user_dict"]:
            logging.warning(f"⚠️ User {user_id} không tồn tại trong dữ liệu")
            return jsonify({"user_id": user_id, "recommendations": []})

        # Lấy sản phẩm cuối cùng của người dùng
        conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')
        cursor = conn.cursor()
        cursor.execute("SELECT product_id FROM user_behavior WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1", (user_id,))
        last_product = cursor.fetchone()
        conn.close()

        state = get_state(user_id, last_product[0] if last_product else None)
        q_values = model.predict(np.array([state]))[0]
        product_array = np.array(list(global_data["product_dict"].keys()))
        recommended_products = product_array[np.argsort(q_values)[::-1][:200]].tolist()  # Top 10 sản phẩm

        logging.info(f"✅ Gợi ý cho user {user_id}: {recommended_products}")
        return jsonify({"user_id": user_id, "recommendations": recommended_products})

    except Exception as e:
        logging.error(f"❌ Lỗi: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/update_policy', methods=['POST'])
def update_policy():
    global model
    try:
        data = request.json
        user_id = int(data.get("user_id"))
        product_id = data.get("product_id")
        reward = float(data.get("reward"))

        # Cập nhật dữ liệu toàn cục
        if time.time() - global_data["last_updated"] > 60:
            old_state_dim = global_data["state_dim"]
            update_global_data()
            if model.state_dim != global_data["state_dim"]:
                logging.warning(f"⚠️ state_dim thay đổi: cũ={model.state_dim}, mới={global_data['state_dim']}")
                old_model = model
                model = DQNModel(global_data["state_dim"], global_data["action_dim"])
                # Chuyển giao trọng số
                old_weights = old_model.model.get_weights()
                new_weights = model.model.get_weights()
                for i in range(len(old_weights)):
                    if old_weights[i].shape == new_weights[i].shape:
                        new_weights[i] = old_weights[i]
                    else:
                        if i == 0:
                            old_shape = old_weights[i].shape
                            new_weights[i][:old_shape[0], :old_shape[1]] = old_weights[i]
                        elif i == 1:
                            new_weights[i][:old_weights[i].shape[0]] = old_weights[i]
                model.model.set_weights(new_weights)
                logging.info("✅ Đã chuyển giao trọng số sang mô hình mới")

        if user_id not in global_data["user_dict"] or product_id not in global_data["product_dict"]:
            return jsonify({"error": "User hoặc sản phẩm không tồn tại"}), 400

        conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')
        cursor = conn.cursor()
        cursor.execute("SELECT product_id FROM user_behavior WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1", (user_id,))
        last_product = cursor.fetchone()
        conn.close()

        state = get_state(user_id, last_product[0] if last_product else None)
        next_state = get_state(user_id, product_id)
        action = global_data["product_dict"][product_id]

        q_targets = model.predict(np.array([state]))
        q_next = model.target_model.predict(np.array([next_state]))
        q_targets[0, action] = reward + 0.9 * np.max(q_next[0])
        model.train(np.array([state]), q_targets, batch_size=1)
        model.update_target()

        product_array = np.array(list(global_data["product_dict"].keys()))
        recommendations = product_array[np.argsort(model.predict(np.array([next_state]))[0])[::-1][:200]].tolist()

        model.save()
        logging.info(f"✅ Cập nhật policy cho user {user_id}: {recommendations}")
        return jsonify({"user_id": user_id, "product_id": product_id, "recommendations": recommendations})

    except Exception as e:
        logging.error(f"❌ Lỗi: {e}")
        return jsonify({"error": str(e)}), 500
# sử dụng trong báo cáo
if __name__ == '__main__':
    app.run(debug=True)