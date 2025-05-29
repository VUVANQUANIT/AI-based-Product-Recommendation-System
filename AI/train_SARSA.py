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
import time
from datetime import datetime
import json

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kết nối MySQL toàn cục
conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')

# Hàng đợi replay buffer toàn cục
replay_buffer = deque(maxlen=2000)

class SARSAModel:
    def __init__(self, state_dim, action_dim):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.model = keras.Sequential([
            layers.Input(shape=(state_dim,)),
            layers.Dense(256, activation="relu"),
            layers.Dense(256, activation="relu"),
            layers.Dense(action_dim, activation="linear")
        ])
        self.optimizer = keras.optimizers.Adam(learning_rate=0.001)
        self.gamma = 0.99
        self.epsilon = 0.3
        self.batch_size = 32

    def predict(self, state):
        try:
            state_tensor = tf.convert_to_tensor(np.array([state], dtype=np.float32), dtype=tf.float32)
            if state_tensor.shape[1] != self.state_dim:
                raise ValueError(f"Kích thước state không khớp: nhận {state_tensor.shape[1]}, kỳ vọng {self.state_dim}")
            return self.model(state_tensor, training=False)[0].numpy()
        except Exception as e:
            logging.error(f"Lỗi trong predict: {e}")
            raise

    def get_action(self, state):
        try:
            if state.shape[0] != self.state_dim:
                logging.error(f"State shape không khớp: {state.shape[0]} vs {self.state_dim}")
                return random.randint(0, self.action_dim - 1)
            if random.random() < self.epsilon:
                return random.randint(0, self.action_dim - 1)
            q_values = self.predict(state)
            return np.argmax(q_values)
        except Exception as e:
            logging.error(f"Lỗi trong get_action: {e}")
            return random.randint(0, self.action_dim - 1)

    def train(self, states, actions, rewards, next_states, next_actions):
        states = np.array(states, dtype=np.float32)
        next_states = np.array(next_states, dtype=np.float32)
        with tf.GradientTape() as tape:
            q_values = self.model(states, training=True)
            next_q_values = self.model(next_states, training=True)
            targets = q_values.numpy()
            for i in range(len(actions)):
                targets[i, actions[i]] = rewards[i] + self.gamma * next_q_values[i, next_actions[i]]
            loss = tf.reduce_mean(tf.square(targets - q_values))
        grads = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

    def save(self, filename="sarsa_model.keras"):
        self.model.save(filename)
        with open("model_config.json", "w") as f:
            json.dump({"state_dim": self.state_dim, "action_dim": self.action_dim}, f)
        logging.info(f"✅ Đã lưu mô hình vào {filename}")

    def load(self, filename="sarsa_model.keras"):
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
    global_data["state_dim"] = len(global_data["user_dict"]) + 10 * len(global_data["product_dict"]) + len(global_data["product_dict"]) + len(global_data["category_dict"]) + 1
    global_data["action_dim"] = len(global_data["product_dict"])
    global_data["last_updated"] = time.time()
    logging.info(f"Đã cập nhật dữ liệu toàn cục: state_dim={global_data['state_dim']}, action_dim={global_data['action_dim']}")

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
        logging.info(f"✅ Đã lấy dữ liệu từ MySQL: {len(data)} bản ghi")
        return data
    except pymysql.Error as e:
        logging.error(f"❌ Lỗi kết nối MySQL: {e}")
        return []

def get_state(user_id, history=None, new_product=None, new_reward=None):
    state = np.zeros(global_data["state_dim"], dtype=np.float32)
    if user_id in global_data["user_dict"]:
        state[global_data["user_dict"][user_id]] = 1

    if history is None:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ub.product_id, SUM(ub.score) as total_score, COUNT(*) as interaction_count, MAX(ub.timestamp) as last_timestamp, p.category_id
            FROM user_behavior ub 
            JOIN product p ON ub.product_id = p.product_id 
            WHERE ub.user_id = %s 
            GROUP BY ub.product_id, p.category_id
            ORDER BY last_timestamp DESC LIMIT %s
        """, (user_id, 9 if new_product else 10))
        history = cursor.fetchall()
    else:
        history = history[-10:] if len(history) > 10 else history

    for i, item in enumerate(history):
        if len(item) == 5:
            prod, total_score, count, ts, cat = item
        elif len(item) == 4:
            prod, total_score, cat, ts = item
            count = sum(1 for h in history if h[0] == prod)
        else:
            continue

        if prod in global_data["product_dict"]:
            idx = global_data["product_dict"][prod]
            state[len(global_data["user_dict"]) + (i + (1 if new_product else 0)) * global_data["action_dim"] + idx] = total_score
            state[len(global_data["user_dict"]) + 10 * global_data["action_dim"] + idx] = count
        if cat in global_data["category_dict"]:
            state[len(global_data["user_dict"]) + 10 * global_data["action_dim"] + len(global_data["product_dict"]) + global_data["category_dict"][cat]] = 1

    if new_product and new_product in global_data["product_dict"]:
        idx = global_data["product_dict"][new_product]
        state[len(global_data["user_dict"]) + 0 * global_data["action_dim"] + idx] = new_reward / 10 if new_reward is not None else 1
        state[len(global_data["user_dict"]) + 10 * global_data["action_dim"] + idx] += 1
        cursor = conn.cursor()
        cursor.execute("SELECT category_id FROM product WHERE product_id = %s", (new_product,))
        cat = cursor.fetchone()
        if cat and cat[0] in global_data["category_dict"]:
            state[len(global_data["user_dict"]) + 10 * global_data["action_dim"] + len(global_data["product_dict"]) + global_data["category_dict"][cat[0]]] = 1

    if history or new_product:
        latest_ts = history[0][3] if history else datetime.now()
        state[-1] = (datetime.now() - latest_ts).total_seconds() / 86400
    else:
        state[-1] = 0

    return state

# Khởi tạo mô hình
update_global_data()
model = SARSAModel(global_data["state_dim"], global_data["action_dim"])
if os.path.exists("sarsa_model.keras") and os.path.exists("model_config.json"):
    with open("model_config.json", "r") as f:
        config = json.load(f)
        if config["state_dim"] == global_data["state_dim"] and config["action_dim"] == global_data["action_dim"]:
            model.load()
        else:
            logging.warning(f"⚠️ state_dim không khớp: cũ={config['state_dim']}, mới={global_data['state_dim']}")
            old_model = SARSAModel(config["state_dim"], config["action_dim"])
            old_model.load()
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
else:
    logging.info(f"✅ Tạo mô hình mới với state_dim={global_data['state_dim']}")

app = Flask(__name__)
CORS(app)

def get_recommendations(user_id, top_k=200):
    global model
    if user_id not in global_data["user_dict"]:
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, SUM(score) as total_score FROM user_behavior GROUP BY product_id ORDER BY total_score DESC LIMIT %s", (top_k,))
        popular = [row[0] for row in cursor.fetchall()]
        return popular if popular else random.sample(list(global_data["product_dict"].keys()), min(top_k, len(global_data["product_dict"])))

    state = get_state(user_id)
    if np.sum(state) == 1:
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, SUM(score) as total_score FROM user_behavior GROUP BY product_id ORDER BY total_score DESC LIMIT %s", (top_k,))
        popular = [row[0] for row in cursor.fetchall()]
        return popular if popular else random.sample(list(global_data["product_dict"].keys()), min(top_k, len(global_data["product_dict"])))

    q_values = model.predict(state)
    product_array = list(global_data["product_dict"].keys())
    total_scores = state[len(global_data["user_dict"]) + 10 * global_data["action_dim"]:len(global_data["user_dict"]) + 10 * global_data["action_dim"] + len(global_data["product_dict"])]
    scores = [(pid, q_val + total_scores[global_data["product_dict"][pid]] * 0.1) for pid, q_val in zip(product_array, q_values)]
    scores.sort(key=lambda x: x[1], reverse=True)
    
    cursor = conn.cursor()
    cursor.execute("SELECT product_id FROM user_behavior WHERE user_id = %s AND action_type = 'remove_from_cart'", (user_id,))
    ignored = {row[0] for row in cursor.fetchall()}
    
    recommendations = [int(pid) for pid, _ in scores if pid not in ignored][:top_k]
    return recommendations

@app.route('/update_policy', methods=['POST'])
def update_policy():
    global model, replay_buffer
    try:
        data = request.json
        user_id = int(data.get("user_id"))
        product_id = data.get("product_id")
        action_type = data.get("action_type")
        reward = float(data.get("reward")) * 10

        if time.time() - global_data["last_updated"] > 60:
            update_global_data()
            if model.state_dim != global_data["state_dim"]:
                logging.warning(f"⚠️ state_dim thay đổi: cũ={model.state_dim}, mới={global_data['state_dim']}")
                old_model = model
                model = SARSAModel(global_data["state_dim"], global_data["action_dim"])
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

        if not all([user_id in global_data["user_dict"], product_id in global_data["product_dict"], reward is not None]):
            return jsonify({"error": "Dữ liệu không hợp lệ"}), 400

        state = get_state(user_id)
        action = global_data["product_dict"][product_id]
        next_state = get_state(user_id, new_product=product_id, new_reward=reward)
        next_action = model.get_action(next_state)

        replay_buffer.append((state, action, reward, next_state, next_action))

        if len(replay_buffer) >= model.batch_size:
            batch = random.sample(replay_buffer, model.batch_size)
            states, actions, rewards, next_states, next_actions = zip(*batch)
            model.train(states, actions, rewards, next_states, next_actions)
            logging.info(f"Đã huấn luyện SARSA với batch {model.batch_size} mẫu")

        model.save()
        recommendations = get_recommendations(user_id, top_k=200)
        logging.info(f"📦 Gợi ý mới cho user {user_id} sau hành động '{action_type}' trên {product_id}: {recommendations[:50]}... (tổng {len(recommendations)})")
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

@app.route('/recommend', methods=['GET'])
def recommend():
    global model
    try:
        user_id = int(request.args.get('user_id', 0))
        if time.time() - global_data["last_updated"] > 60:
            update_global_data()
            if model.state_dim != global_data["state_dim"]:
                logging.warning(f"⚠️ state_dim thay đổi: cũ={model.state_dim}, mới={global_data['state_dim']}")
                old_model = model
                model = SARSAModel(global_data["state_dim"], global_data["action_dim"])
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

        recommendations = get_recommendations(user_id, top_k=200)
        logging.info(f"📦 Gợi ý cho user {user_id}: {recommendations[:50]}... (tổng {len(recommendations)})")
        return jsonify({"user_id": user_id, "recommendations": recommendations})
    except Exception as e:
        logging.error(f"❌ Lỗi: {e}")
        return jsonify({"error": str(e)}), 500

def train_sarsa(model, data, episodes=20, max_records=None):
    user_history = {}
    for user_id, product_id, action_type, reward, category_id, timestamp in data:
        if user_id not in user_history:
            user_history[user_id] = []
        user_history[user_id].append((product_id, reward, category_id, timestamp))

    # Giới hạn số lượng bản ghi nếu cần
    data_to_process = data[:max_records] if max_records else data
    logging.info(f"Xử lý {len(data_to_process)}/{len(data)} bản ghi")

    for i, (user_id, product_id, action_type, reward, category_id, timestamp) in enumerate(data_to_process):
        if i % 100 == 0:  # Log tiến trình
            logging.info(f"Đã xử lý {i}/{len(data_to_process)} bản ghi")
        try:
            prev_history = user_history[user_id][:i] if i > 0 else []
            state = get_state(user_id, history=prev_history)
            action = global_data["product_dict"][product_id]
            next_history = user_history[user_id][:i+1]
            next_state = get_state(user_id, history=next_history[:-1], new_product=product_id, new_reward=reward * 10)
            next_action = model.get_action(next_state)
            replay_buffer.append((state, action, reward * 10, next_state, next_action))
        except Exception as e:
            logging.error(f"Lỗi khi xử lý user_id={user_id}, product_id={product_id}: {e}")
            continue

    for episode in range(episodes):
        if len(replay_buffer) >= model.batch_size:
            batch = random.sample(replay_buffer, model.batch_size)
            states, actions, rewards, next_states, next_actions = zip(*batch)
            model.train(states, actions, rewards, next_states, next_actions)
            logging.info(f"🔄 Episode {episode + 1}/{episodes}")
        else:
            logging.warning(f"Không đủ dữ liệu trong replay_buffer: {len(replay_buffer)}/{model.batch_size}")
    model.save()

# Huấn luyện ban đầu
data = get_data()
train_sarsa(model, data, episodes=20) # Dùng tất cả bản ghi để huấn luyện ban đầu

if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        conn.close()