import os
from graphviz import Digraph

# Thêm đường dẫn Graphviz vào PATH (cập nhật theo máy của bạn)
os.environ["PATH"] += os.pathsep + 'C:/Users/quanc/Downloads/windows_10_cmake_Release_Graphviz-12.2.1-win64/Graphviz-12.2.1-win64/bin'

# Tạo đối tượng lưu đồ
dot = Digraph(comment='DQN Recommendation System Flowchart', format='png', engine='dot')
dot.attr(rankdir='TB', size='12,20')  # Hướng từ trên xuống, kích thước 12x20 inch
dot.attr('node', fontsize='10', fontname='Arial')  # Font chữ nhỏ và rõ ràng
dot.attr('edge', fontsize='8')  # Font nhãn cạnh nhỏ hơn

# Bắt đầu (màu hồng nhạt, hình elip)
dot.attr('node', shape='ellipse', style='filled', fillcolor='lightpink')
dot.node('A', 'Bắt đầu')

# Quy trình lấy dữ liệu (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('B', 'Lấy dữ liệu từ MySQL\n(user_id, product_id,\naction_type, score,\ntimestamp)')

# Cập nhật dữ liệu toàn cục (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('C', 'Cập nhật global_data\n(user_dict, product_dict,\nstate_dim, action_dim)')

# Khởi tạo mô hình DQN (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('D', 'Khởi tạo mô hình DQN\n(128-128-linear, state_dim,\naction_dim, replay_buffer=1000)')

# Kiểm tra mô hình cũ (màu vàng nhạt, hình thoi)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('E', 'Tồn tại mô hình cũ\n(dqn_model.keras)?')

# Load mô hình cũ (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('F', 'Load mô hình cũ\n(Chuyển giao trọng số\nnếu state_dim thay đổi)')

# Chuẩn bị dữ liệu huấn luyện (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('G', 'Chuẩn bị dữ liệu huấn luyện\n(state, action, reward,\nnext_state từ lịch sử)')

# Huấn luyện DQN (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('H', 'Huấn luyện DQN\n(10 episodes, batch_size=32,\nepsilon_decay=0.99, gamma=0.9)')
dot.node('I', 'Lưu mô hình\n(dqn_model.keras,\ndqn_config.json)')

# API /recommend (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('J', 'Nhận yêu cầu /recommend\n(user_id)')

# Kiểm tra user_id (màu vàng nhạt, hình thoi)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('K', 'User_id có trong\nuser_dict không?')

# Trả về rỗng (màu đỏ nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('L', 'Trả về JSON\n(recommendations rỗng)')

# Cập nhật global_data nếu cần (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('M', 'Cập nhật global_data\n(nếu quá 60 giây,\nchuyển giao trọng số nếu cần)')

# Tạo state (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('N', 'Lấy sản phẩm cuối cùng\nvà tạo state\n(user_id, last_product_id)')

# Dự đoán và gợi ý (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('O', 'Dự đoán Q-values\n(model.predict(state))')
dot.node('P', 'Sắp xếp Q-values\nvà chọn top 200 sản phẩm')

# Trả về kết quả (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('Q', 'Trả về JSON\n(user_id, recommendations)')

# API /update_policy (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('R', 'Nhận yêu cầu /update_policy\n(user_id, product_id, reward)')

# Kiểm tra user_id và product_id (màu vàng nhạt, hình thoi)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('S', 'User_id và product_id\ncó trong dữ liệu không?')

# Trả về lỗi (màu đỏ nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('T', 'Trả về lỗi\n(user/sản phẩm không tồn tại)')

# Cập nhật policy (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('U', 'Cập nhật global_data\n(nếu quá 60 giây,\nchuyển giao trọng số nếu cần)')
dot.node('V', 'Tạo state, next_state\nvà cập nhật Q-values')
dot.node('W', 'Huấn luyện mô hình\nvà lưu mô hình')
dot.node('X', 'Dự đoán và trả về\nrecommendations mới')

# Kết thúc (màu hồng nhạt, hình elip)
dot.attr('node', shape='ellipse', style='filled', fillcolor='lightpink')
dot.node('Y', 'Kết urged')

# Liên kết các nút
dot.edge('A', 'B')
dot.edge('B', 'C')
dot.edge('C', 'D')
dot.edge('D', 'E')
dot.edge('E', 'F', label='Có')
dot.edge('E', 'G', label='Không')
dot.edge('F', 'G')
dot.edge('G', 'H')
dot.edge('H', 'I')
dot.edge('I', 'J', style='dashed', label='API /recommend')
dot.edge('I', 'R', style='dashed', label='API /update_policy')
dot.edge('J', 'K')
dot.edge('K', 'L', label='Không')
dot.edge('K', 'M', label='Có')
dot.edge('M', 'N')
dot.edge('N', 'O')
dot.edge('O', 'P')
dot.edge('P', 'Q')
dot.edge('Q', 'Y', style='dotted', label='Hoàn tất /recommend')
dot.edge('L', 'Y', style='dotted', label='Hoàn tất /recommend\n(rỗng)')
dot.edge('R', 'S')
dot.edge('S', 'T', label='Không')
dot.edge('S', 'U', label='Có')
dot.edge('U', 'V')
dot.edge('V', 'W')
dot.edge('W', 'X')
dot.edge('X', 'Y', style='dotted', label='Hoàn tất /update_policy')
dot.edge('T', 'Y', style='dotted', label='Hoàn tất /update_policy\n(lỗi)')

# Render lưu đồ
dot.render('dqn_recommendation_flowchart', view=True)
print("Lưu đồ đã được tạo và lưu dưới dạng 'dqn_recommendation_flowchart.png'")