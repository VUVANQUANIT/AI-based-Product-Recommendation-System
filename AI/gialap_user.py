import pymysql
import random
from datetime import datetime, timedelta

# Kết nối database
try:
    conn = pymysql.connect(host='localhost', user='root', password='', database='thoitrang')
    cursor = conn.cursor()
except pymysql.Error as e:
    print(f"Lỗi kết nối database: {e}")
    exit()

# Mảng điểm
points = {
    'click': 2,
    'search': 1,
    'add_to_cart': 5,
    'purchase': 10,
    'remove_from_cart': -15,
    'decrease_quantity': -3
}

# Lấy danh sách user_id từ bảng users
cursor.execute("SELECT user_id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]
if not user_ids:
    print("Không có user_id trong bảng users. Vui lòng thêm dữ liệu trước!")
    conn.close()
    exit()
print(f"Số lượng user_id: {len(user_ids)}")

# Lấy danh sách product_id từ bảng product
cursor.execute("SELECT product_id FROM product")
product_ids = [row[0] for row in cursor.fetchall()]
if not product_ids:
    print("Không có product_id trong bảng product. Vui lòng thêm dữ liệu trước!")
    conn.close()
    exit()
print(f"Số lượng product_id: {len(product_ids)}")

# Hàm tạo timestamp ngẫu nhiên trong 7 ngày gần nhất
def random_timestamp():
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)
    time_diff = random.uniform(0, (now - seven_days_ago).total_seconds())
    return seven_days_ago + timedelta(seconds=time_diff)

# Hàm kiểm tra và cập nhật hoặc thêm mới
def update_or_insert(user_id, product_id, action_type):
    try:
        cursor.execute("""
            SELECT score, timestamp 
            FROM user_behavior 
            WHERE user_id = %s AND product_id = %s AND action_type = %s
            ORDER BY timestamp DESC LIMIT 1
        """, (user_id, product_id, action_type))
        result = cursor.fetchone()

        current_time = random_timestamp()  # Timestamp ngẫu nhiên trong 7 ngày
        if result:  # Nếu đã tồn tại
            current_score = result[0]
            new_score = current_score + points[action_type]
            cursor.execute("""
                UPDATE user_behavior 
                SET score = %s, timestamp = %s 
                WHERE user_id = %s AND product_id = %s AND action_type = %s
            """, (new_score, current_time, user_id, product_id, action_type))
        else:  # Nếu chưa tồn tại, thêm mới
            score = points[action_type]
            cursor.execute("""
                INSERT INTO user_behavior (user_id, product_id, action_type, score, timestamp) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, product_id, action_type, score, current_time))
    except pymysql.Error as e:
        print(f"Lỗi khi xử lý user_id={user_id}, product_id={product_id}, action_type={action_type}: {e}")

# Tạo hoặc cập nhật 50,000 bản ghi giả lập
print("Bắt đầu tạo 50,000 bản ghi giả lập...")
for i in range(50000):
    user_id = random.choice(user_ids)  # Chọn ngẫu nhiên từ user_ids có thật
    product_id = random.choice(product_ids)  # Chọn ngẫu nhiên từ product_ids có thật
    action_type = random.choice(list(points.keys()))
    update_or_insert(user_id, product_id, action_type)
    if (i + 1) % 10000 == 0:  # Báo tiến độ mỗi 10,000 bản ghi
        print(f"Đã xử lý {i + 1}/50000 bản ghi")

try:
    conn.commit()
    print("Đã cập nhật/thêm 50,000 bản ghi với timestamp trong 7 ngày gần nhất!")
except pymysql.Error as e:
    print(f"Lỗi khi commit: {e}")
finally:
    conn.close()