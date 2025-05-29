# Danh sách các dòng log được trích xuất từ hình ảnh
log_entries = [
    "2025-04-08 15:22:21,040 INFO - Q-table loaded from mysql",
    "2025-04-08 15:22:21,849 INFO - Initial Q-table training completed",
    "2025-04-08 15:22:52,686 INFO - Serving Flask app 'train_q_learning.ver3'",
    "2025-04-08 15:22:52,686 WARNING - This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.",
    "2025-04-08 15:22:52,686 INFO - Running on http://127.0.0.1:5000",
    "2025-04-08 15:22:52,686 INFO - Press CTRL+C to quit",
    "2025-04-08 15:29:08,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:08] GET / HTTP/1.1 200 -",
    "2025-04-08 15:29:09,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:09] GET /api HTTP/1.1 200 -",
    "2025-04-08 15:29:10,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:10] GET /recommenduser-id=20 HTTP/1.1 200 -",
    "2025-04-08 15:29:11,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:11] POST /update_policy HTTP/1.1 200 -",
    "2025-04-08 15:29:12,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:12] GET /recommenduser-id=21 HTTP/1.1 200 -",
    "2025-04-08 15:29:13,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:13] POST /update_policy HTTP/1.1 200 -",
    "2025-04-08 15:29:14,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:14] GET /recommenduser-id=22 HTTP/1.1 200 -",
    "2025-04-08 15:29:15,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:15] POST /update_policy HTTP/1.1 200 -",
    "2025-04-08 15:29:16,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:16] GET /recommenduser-id=23 HTTP/1.1 200 -",
    "2025-04-08 15:29:17,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:17] POST /update_policy HTTP/1.1 200 -",
    "2025-04-08 15:29:18,654 INFO - 127.0.0.1 - - [08/Apr/2025 15:29:18] GET /recommenduser-id=24 HTTP/1.1 200 -"
]

# Hàm in danh sách log theo định dạng
def print_logs(log_list):
    print("=== LOG LIST ===")
    for index, entry in enumerate(log_list, 1):
        # Tách thời gian, mức độ log (INFO/WARNING), và nội dung
        parts = entry.split(" - ", 2)  # Tách thành 3 phần: thời gian, mức độ, nội dung
        if len(parts) >= 2:
            timestamp = parts[0]
            level_content = parts[1].split(" ", 1)
            if len(level_content) >= 2:
                level = level_content[0]
                content = level_content[1]
                print(f"{index}. [{timestamp}] [{level}] {content}")
            else:
                print(f"{index}. [{timestamp}] {entry}")
        else:
            print(f"{index}. {entry}")
    print("===============")

# Gọi hàm để in danh sách
print_logs(log_entries)