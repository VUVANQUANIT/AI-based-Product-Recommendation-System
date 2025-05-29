import os
from graphviz import Digraph

# Thêm đường dẫn Graphviz vào PATH (thay đổi theo đường dẫn của bạn)
os.environ["PATH"] += os.pathsep + 'C:/Users/quanc/Downloads/windows_10_cmake_Release_Graphviz-12.2.1-win64/Graphviz-12.2.1-win64/bin'

# Tạo đối tượng lưu đồ
dot = Digraph(comment='Q-Learning Recommendation System Flowchart', format='png')
dot.attr(rankdir='TB', size='15,25')  # Kích thước: 15 inch rộng, 25 inch cao
dot.attr('node', fontsize='10')  # Font nhỏ để tránh chồng lấn

# Bắt đầu (màu hồng nhạt, căn giữa)
dot.attr('node', shape='ellipse', style='filled', fillcolor='lightpink')
dot.node('A', 'Bắt đầu', _attributes={'pos': '0,0!'})  # Căn giữa trên cùng

# Khởi tạo (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('B', 'Kết nối MySQL')
dot.node('C', 'Khởi tạo Q-table\n(defaultdict)')
dot.node('D', 'Lấy tất cả product_id\ntừ bảng product')

# Tải và huấn luyện ban đầu (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('E', 'Tải Q-table từ MySQL\n(q_table)')
dot.node('F', 'Huấn luyện ban đầu Q-table\ntừ user_behavior\n(Q = Q + α * (r - Q))')
dot.node('G', 'Lưu Q-value vào MySQL\n(q_table)')

# API /recommend (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('H', 'Nhận yêu cầu /recommend\n(user_id, page, limit)')

# Kiểm tra dữ liệu yêu cầu (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('I', 'Dữ liệu yêu cầu\nhợp lệ?')

# Báo lỗi (màu đỏ nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('J', 'Báo lỗi: Thiếu user_id\nhoặc user_id không hợp lệ')

# Tạo state (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('K', 'Tạo state\n(user_id + category_id gần nhất)')

# Kiểm tra epsilon (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('L', 'Khám phá\n(rand < epsilon)?')

# Gợi ý ngẫu nhiên (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('M', 'Chọn ngẫu nhiên\n36 sản phẩm')

# Gợi ý khai thác (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('N', 'Sắp xếp sản phẩm\ntheo Q-value giảm dần')
dot.node('O', 'Bổ sung ngẫu nhiên\nnếu không đủ 36')

# Phân trang và trả về (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('P', 'Phân trang\n(page, limit)')
dot.node('Q', 'Trả về JSON\n(recommendations)')

# API /update_policy (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('R', 'Nhận yêu cầu /update_policy\n(user_id, product_id,\naction_type, reward)')

# Cập nhật Q-table (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('S', 'Tạo state\n(user_id + category_id gần nhất)')
dot.node('T', 'Cập nhật Q-value\n(Q = Q + α * (r + γ * max(Q_next) - Q))')
dot.node('U', 'Lưu Q-value vào MySQL\n(q_table)')
dot.node('V', 'Giảm epsilon\n(epsilon = max(epsilon_min,\nepsilon * epsilon_decay))')

# Kết thúc (màu hồng nhạt, không viền cụm, căn giữa)
dot.attr('node', shape='ellipse', style='filled', fillcolor='lightpink')
dot.node('W', 'Kết thúc', _attributes={'pos': '0,-25!'})  # Căn giữa dưới cùng

# Liên kết các nút
dot.edge('A', 'B')
dot.edge('B', 'C')
dot.edge('C', 'D')
dot.edge('D', 'E')
dot.edge('E', 'F')
dot.edge('F', 'G')
dot.edge('G', 'H', style='dashed', label='API /recommend')
dot.edge('G', 'R', style='dashed', label='API /update_policy')
dot.edge('H', 'I')
dot.edge('I', 'J', label='Không')
dot.edge('I', 'K', label='Có')
dot.edge('K', 'L')
dot.edge('L', 'M', label='Có')
dot.edge('L', 'N', label='Không')
dot.edge('N', 'O')
dot.edge('M', 'P')
dot.edge('O', 'P')
dot.edge('P', 'Q')
dot.edge('R', 'S')
dot.edge('S', 'T')
dot.edge('T', 'U')
dot.edge('U', 'V')

# Liên kết đến "Kết thúc" với nét đứt
dot.edge('J', 'W', style='dotted', label='Hoàn tất lỗi\n/recommend', constraint='true', weight='10')
dot.edge('Q', 'W', style='dotted', label='Hoàn tất\n/recommend', constraint='true', weight='10')
dot.edge('V', 'W', style='dotted', label='Hoàn tất\n/update_policy', constraint='true', weight='10')

# Render lưu đồ
dot.render('q_learning_recommendation_flowchart', view=True)
print("Lưu đồ đã được tạo và lưu dưới dạng 'q_learning_recommendation_flowchart.png'")