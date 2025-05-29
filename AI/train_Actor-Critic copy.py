import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import pymysql
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from collections import deque
import random
from datetime import datetime
import threading
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

global_data = {
    "user_ids": [],
    "product_ids": [],
    "category_ids": [],
    "user_id_to_index": {},
    "product_id_to_index": {},
    "category_id_to_index": {},
    "state_dim": 0,
    "action_dim": 0,
    "last_updated": 0
}

def get_data():
    try:
        conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ub.user_id, ub.product_id, ub.action_type, ub.score, p.category_id, ub.timestamp
            FROM user_behavior ub
            JOIN product p ON ub.product_id = p.product_id
            ORDER BY ub.user_id, ub.timestamp
        """)
        data = cursor.fetchall()
        conn.close()
        return data
    except pymysql.Error as e:
        logging.error(f"Lỗi kết nối MySQL: {e}")
        return []

def update_global_data():
    data = get_data()
    global_data["user_ids"] = sorted(set(d[0] for d in data))
    global_data["product_ids"] = sorted(set(d[1] for d in data))
    global_data["category_ids"] = sorted(set(d[4] for d in data))
    global_data["user_id_to_index"] = {uid: idx for idx, uid in enumerate(global_data["user_ids"])}
    global_data["product_id_to_index"] = {pid: idx for idx, pid in enumerate(global_data["product_ids"])}
    global_data["category_id_to_index"] = {cid: idx for idx, cid in enumerate(global_data["category_ids"])}
    global_data["state_dim"] = len(global_data["user_ids"]) + len(global_data["product_ids"]) + len(global_data["category_ids"]) + 1
    global_data["action_dim"] = len(global_data["product_ids"])
    global_data["last_updated"] = time.time()
    logging.info("Đã cập nhật dữ liệu toàn cục")

class ActorCritic:
    def __init__(self, state_dim, action_dim):
        self.actor = tf.keras.Sequential([
            layers.Input(shape=(state_dim,)),
            layers.Dense(128, activation='relu'),
            layers.LayerNormalization(),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dense(action_dim, activation='softmax')
        ])
        self.critic = tf.keras.Sequential([
            layers.Input(shape=(state_dim,)),
            layers.Dense(128, activation='relu'),
            layers.LayerNormalization(),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dense(1)
        ])
        self.target_actor = tf.keras.models.clone_model(self.actor)
        self.target_critic = tf.keras.models.clone_model(self.critic)
        self.target_actor.set_weights(self.actor.get_weights())
        self.target_critic.set_weights(self.critic.get_weights())
        self.actor_optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
        self.critic_optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
        self.replay_buffer = deque(maxlen=500)
        self.tau = 0.005

    def train_batch(self, batch_size=32, gamma=0.9):
        if len(self.replay_buffer) < batch_size:
            return
        batch = random.sample(self.replay_buffer, batch_size)
        states = np.array([x[0] for x in batch], dtype=np.float32)
        actions = [x[1] for x in batch]
        rewards = np.array([x[2] for x in batch], dtype=np.float32)
        next_states = np.array([x[3] for x in batch], dtype=np.float32)

        with tf.GradientTape() as actor_tape:
            action_probs = self.actor(states, training=True)
            critic_values = self.critic(states, training=True)
            next_critic_values = self.target_critic(next_states, training=True)
            td_targets = rewards + gamma * next_critic_values
            td_errors = td_targets - critic_values
            actor_loss = -tf.reduce_mean([tf.math.log(action_probs[i, actions[i]] + 1e-10) * td_errors[i] for i in range(batch_size)])
        actor_grads = actor_tape.gradient(actor_loss, self.actor.trainable_variables)
        self.actor_optimizer.apply_gradients(zip(actor_grads, self.actor.trainable_variables))

        with tf.GradientTape() as critic_tape:
            critic_values = self.critic(states, training=True)
            critic_loss = tf.reduce_mean(tf.square(td_targets - critic_values))
        critic_grads = critic_tape.gradient(critic_loss, self.critic.trainable_variables)
        self.critic_optimizer.apply_gradients(zip(critic_grads, self.critic.trainable_variables))

        self.update_target_networks()

    def update_target_networks(self):
        actor_weights = self.actor.get_weights()
        critic_weights = self.critic.get_weights()
        target_actor_weights = self.target_actor.get_weights()
        target_critic_weights = self.target_critic.get_weights()
        for i in range(len(actor_weights)):
            target_actor_weights[i] = self.tau * actor_weights[i] + (1 - self.tau) * target_actor_weights[i]
        for i in range(len(critic_weights)):
            target_critic_weights[i] = self.tau * critic_weights[i] + (1 - self.tau) * target_critic_weights[i]
        self.target_actor.set_weights(target_actor_weights)
        self.target_critic.set_weights(target_critic_weights)

    def save(self):
        self.actor.save("actor.keras")
        self.critic.save("critic.keras")
        logging.info("Đã lưu mô hình Actor-Critic")

    def load(self):
        try:
            self.actor = tf.keras.models.load_model("actor.keras")
            self.critic = tf.keras.models.load_model("critic.keras")
            self.target_actor = tf.keras.models.clone_model(self.actor)
            self.target_critic = tf.keras.models.clone_model(self.critic)
            self.target_actor.set_weights(self.actor.get_weights())
            self.target_critic.set_weights(self.critic.get_weights())
            self.actor_optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
            self.critic_optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
            logging.info("Đã load mô hình Actor-Critic và tái tạo optimizer")
        except Exception as e:
            logging.warning(f"Không thể load mô hình: {e}, khởi tạo mới")
            self.__init__(global_data["state_dim"], global_data["action_dim"])

update_global_data()
model = ActorCritic(global_data["state_dim"], global_data["action_dim"])

data = get_data()
for user_id, product_id, _, reward, category_id, timestamp in data:
    user_idx = global_data["user_id_to_index"][user_id]
    product_idx = global_data["product_id_to_index"][product_id]
    category_idx = global_data["category_id_to_index"][category_id]
    state = np.zeros(global_data["state_dim"])
    state[user_idx] = 1
    state[len(global_data["user_ids"]) + product_idx] = reward
    state[len(global_data["user_ids"]) + len(global_data["product_ids"]) + category_idx] = reward
    state[-1] = (datetime.now() - timestamp).total_seconds() / 86400
    next_state = state.copy()
    model.replay_buffer.append((state, product_idx, reward, next_state))

for epoch in range(100):
    model.train_batch(batch_size=32)
    if epoch % 20 == 0:
        logging.info(f"Epoch {epoch}/100 hoàn thành")
model.save()

def background_training():
    global model
    while True:
        time.sleep(300)
        update_global_data()
        if global_data["state_dim"] != model.actor.input_shape[1] or global_data["action_dim"] != model.actor.output_shape[1]:
            logging.info("Kích thước thay đổi, khởi tạo lại mô hình")
            model = ActorCritic(global_data["state_dim"], global_data["action_dim"])
            model.replay_buffer.clear()
            data = get_data()
            for u_id, p_id, _, reward, c_id, ts in data:
                u_idx = global_data["user_id_to_index"][u_id]
                p_idx = global_data["product_id_to_index"][p_id]
                c_idx = global_data["category_id_to_index"][c_id]
                state = np.zeros(global_data["state_dim"])
                state[u_idx] = 1
                state[len(global_data["user_ids"]) + p_idx] = reward
                state[len(global_data["user_ids"]) + len(global_data["product_ids"]) + c_idx] = reward
                state[-1] = (datetime.now() - ts).total_seconds() / 86400
                next_state = state.copy()
                model.replay_buffer.append((state, p_idx, reward, next_state))
            for _ in range(20):
                model.train_batch(batch_size=32)
            model.save()
        else:
            data = get_data()
            for u_id, p_id, _, reward, c_id, ts in data:
                if u_id in global_data["user_id_to_index"] and p_id in global_data["product_id_to_index"]:
                    u_idx = global_data["user_id_to_index"][u_id]
                    p_idx = global_data["product_id_to_index"][p_id]
                    c_idx = global_data["category_id_to_index"][c_id]
                    state = np.zeros(global_data["state_dim"])
                    state[u_idx] = 1
                    state[len(global_data["user_ids"]) + p_idx] = reward
                    state[len(global_data["user_ids"]) + len(global_data["product_ids"]) + c_idx] = reward
                    state[-1] = (datetime.now() - ts).total_seconds() / 86400
                    next_state = state.copy()
                    model.replay_buffer.append((state, p_idx, reward, next_state))
            model.train_batch(batch_size=32)
            model.save()
        logging.info("Đã huấn luyện mô hình trong background")

threading.Thread(target=background_training, daemon=True).start()

app = Flask(__name__)
CORS(app)
@app.route('/update_policy', methods=['POST'])
def update_policy():
    try:
        data = request.json
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        action_type = data.get('action_type')
        reward = data.get('reward')

        if not all([user_id, product_id, action_type, reward]):
            return jsonify({"error": "Thiếu thông tin cần thiết"}), 400

        # Thêm vào replay buffer để cập nhật mô hình
        if user_id in global_data["user_id_to_index"] and product_id in global_data["product_id_to_index"]:
            user_idx = global_data["user_id_to_index"][user_id]
            product_idx = global_data["product_id_to_index"][product_id]
            category_id = None  # Lấy từ DB nếu cần
            if category_id in global_data["category_id_to_index"]:
                category_idx = global_data["category_id_to_index"][category_id]
            else:
                category_idx = 0  # Giá trị mặc định nếu không có category_id

            state = np.zeros(global_data["state_dim"])
            state[user_idx] = 1
            state[len(global_data["user_ids"]) + product_idx] = reward
            if category_id:
                state[len(global_data["user_ids"]) + len(global_data["product_ids"]) + category_idx] = reward
            state[-1] = 0  # Hoặc thời gian hiện tại nếu cần

            next_state = state.copy()
            model.replay_buffer.append((state, product_idx, reward, next_state))

            # Huấn luyện ngay nếu buffer đủ lớn
            if len(model.replay_buffer) >= 32:
                model.train_batch(batch_size=32)
                model.save()

            logging.info(f"Đã cập nhật hành vi: user_id={user_id}, product_id={product_id}, action_type={action_type}, reward={reward}")
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"error": "user_id hoặc product_id không tồn tại"}), 400
    except Exception as e:
        logging.error(f"Lỗi khi cập nhật chính sách: {e}")
        return jsonify({"error": str(e)}), 500
@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        user_id = int(request.args.get('user_id', 0))
        num_recommendations = request.args.get('num_recommendations', None)

        if num_recommendations is not None:
            num_recommendations = int(num_recommendations)
            if num_recommendations <= 0 or num_recommendations > global_data["action_dim"]:
                num_recommendations = global_data["action_dim"]

        conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')
        cursor = conn.cursor()

        if user_id not in global_data["user_id_to_index"]:
            logging.warning(f"User {user_id} không tồn tại trong dữ liệu hành vi")
            cursor.execute("""
                SELECT ub.product_id, SUM(ub.score) as total_score
                FROM user_behavior ub
                GROUP BY ub.product_id
                ORDER BY total_score DESC
                LIMIT %s
            """, (num_recommendations or 10,))
            popular_products = [row[0] for row in cursor.fetchall()]
            conn.close()
            if not popular_products:
                popular_products = random.sample(global_data["product_ids"], min(10, len(global_data["product_ids"])))
            return jsonify({"user_id": user_id, "recommendations": popular_products, "total": len(popular_products)})

        model.load()

        # Lấy 10 hành động gần nhất
        cursor.execute("""
            SELECT ub.product_id, AVG(ub.score) as avg_score, COUNT(*) as freq, MAX(ub.timestamp) as latest_timestamp
            FROM user_behavior ub
            WHERE ub.user_id = %s
            ORDER BY ub.timestamp DESC
            LIMIT 10
        """, (user_id,))
        history = cursor.fetchall()

        # Lấy danh sách sản phẩm bị bỏ qua và vừa chọn
        cursor.execute("""
            SELECT product_id, action_type, timestamp
            FROM user_behavior
            WHERE user_id = %s AND action_type IN ('remove_from_cart', 'click')
            ORDER BY timestamp DESC
        """, (user_id,))
        behavior = cursor.fetchall()
        ignored_products = {row[0] for row in behavior if row[1] == "remove_from_cart"}
        clicked_products = {row[0] for row in behavior if row[1] == "click"}
        latest_action = behavior[0] if behavior else None

        # Lấy danh mục phổ biến
        cursor.execute("""
            SELECT p.category_id, SUM(ub.score) as category_score
            FROM user_behavior ub
            JOIN product p ON ub.product_id = p.product_id
            WHERE ub.user_id = %s
            GROUP BY p.category_id
            ORDER BY category_score DESC
            LIMIT 3
        """, (user_id,))
        top_categories = [row[0] for row in cursor.fetchall()]

        state = np.zeros(global_data["state_dim"])
        user_idx = global_data["user_id_to_index"][user_id]
        state[user_idx] = 1
        history_weights = {}
        current_time = datetime.now()
        for product_id, avg_score, freq, latest_timestamp in history:
            avg_score = float(avg_score)
            time_diff = (current_time - latest_timestamp).total_seconds() / 86400
            decay_factor = max(0.1, 1 - 0.1 * time_diff)
            history_weights[product_id] = avg_score * freq * decay_factor
            if product_id in global_data["product_id_to_index"]:
                p_idx = global_data["product_id_to_index"][product_id]
                state[len(global_data["user_ids"]) + p_idx] += avg_score * freq * decay_factor
        state[-1] = random.uniform(0, 1) * len(history)

        action_probs = model.actor.predict(np.array([state]), verbose=0)[0]

        if not history:
            cursor.execute("""
                SELECT ub.product_id, SUM(ub.score) as total_score
                FROM user_behavior ub
                GROUP BY ub.product_id
                ORDER BY total_score DESC
                LIMIT %s
            """, (num_recommendations or 10,))
            recommended_products = [row[0] for row in cursor.fetchall()]
            conn.close()
            if not recommended_products:
                recommended_products = random.sample(global_data["product_ids"], min(10, len(global_data["product_ids"])))
            logging.info(f"User {user_id} không có lịch sử, trả về sản phẩm phổ biến: {recommended_products[:10]}")
            return jsonify({"user_id": user_id, "recommendations": recommended_products, "total": len(recommended_products)})

        final_scores = []
        latest_product_id = latest_action[0] if latest_action else None
        latest_action_type = latest_action[1] if latest_action else None
        for i, product_id in enumerate(global_data["product_ids"]):
            action_prob = action_probs[i]
            history_weight = history_weights.get(product_id, 0)
            recent_weight = 5 if product_id == latest_product_id and latest_action_type == "click" else 0
            cursor.execute("SELECT category_id FROM product WHERE product_id = %s", (product_id,))
            product_category = cursor.fetchone()[0]
            related_weight = 5 if product_category in top_categories else 0
            final_score = (action_prob * 0.5) + (history_weight * 0.3) + (recent_weight * 0.1) + (related_weight * 0.1)
            penalty = -20 if product_id in ignored_products else (-5 if product_id not in clicked_products and history_weight > 0 else 0)
            final_score += penalty
            final_scores.append((product_id, final_score))

        epsilon = 0.02
        if random.random() < epsilon:
            recommended_products = random.sample(global_data["product_ids"], min(global_data["action_dim"], len(global_data["product_ids"])))
        else:
            final_scores.sort(key=lambda x: x[1], reverse=True)
            recommended_products = [product_id for product_id, _ in final_scores if product_id not in ignored_products]

            if latest_product_id and latest_product_id in recommended_products:
                recommended_products.remove(latest_product_id)
                if latest_action_type == "click":
                    recommended_products.insert(0, latest_product_id)

        if num_recommendations is not None:
            recommended_products = recommended_products[:num_recommendations]

        if latest_product_id and len(model.replay_buffer) >= 32:
            reward = 5 if latest_action_type == "click" else float(history[0][1]) if history else 0
            action = global_data["product_id_to_index"][latest_product_id]
            model.replay_buffer.append((state, action, reward, state))
            model.train_batch(batch_size=32)

        conn.close()
        logging.info(f"Gợi ý cho user {user_id}: {recommended_products[:50]} (tổng {len(recommended_products)} sản phẩm)")
        return jsonify({"user_id": user_id, "recommendations": recommended_products, "total": len(final_scores)})
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)