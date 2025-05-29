import os
from graphviz import Digraph

# Thêm đường dẫn Graphviz vào PATH
os.environ["PATH"] += os.pathsep + 'C:/Users/quanc/Downloads/windows_10_cmake_Release_Graphviz-12.2.1-win64/Graphviz-12.2.1-win64/bin'

# Tạo đối tượng lưu đồ
dot = Digraph(comment='SARSA Recommendation System Flowchart', format='png')
dot.attr(rankdir='TB', size='15,30')  # Kích thước: 15 inch rộng, 30 inch cao
dot.attr('node', fontsize='10')  # Font nhỏ để tránh chồng lấn

# Bắt đầu (màu hồng nhạt, căn giữa)
dot.attr('node', shape='ellipse', style='filled', fillcolor='lightpink')
dot.node('A', 'Bắt đầu', _attributes={'pos': '0,0!'})  # Căn giữa trên cùng

# Quy trình lấy dữ liệu (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('B', 'Lấy dữ liệu từ MySQL\n(user_id, product_id,\naction_type, score,\ncategory_id, timestamp)')

# Cập nhật dữ liệu toàn cục (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('C', 'Cập nhật global_data\n(user_dict, product_dict,\ncategory_dict, state_dim,\naction_dim)')

# Kiểm tra mô hình tồn tại (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('D', 'Mô hình SARSA\nđã tồn tại?')

# Khởi tạo mô hình (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('E', 'Khởi tạo mô hình SARSA\n(state_dim, action_dim,\n256-256-linear)')

# Load mô hình (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('F', 'Load mô hình\ntừ sarsa_model.keras')

# Kiểm tra kích thước mô hình (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('G', 'Kích thước mô hình\nkhớp với global_data?')

# Chuyển giao trọng số (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('H', 'Chuyển giao trọng số\ntừ mô hình cũ sang mới')

# Huấn luyện ban đầu (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('I', 'Huấn luyện SARSA ban đầu\n(episodes=20, max_records=1000,\nreplay_buffer, train(states,\nactions, rewards, next_states,\nnext_actions))')
dot.node('J', 'Lưu mô hình\n(sarsa_model.keras)')

# API /recommend (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('K', 'Nhận yêu cầu /recommend\n(user_id từ request)')

# Kiểm tra thời gian cập nhật (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('L', 'Đã quá 60 giây\ntừ lần cập nhật cuối?')

# Cập nhật và kiểm tra state_dim (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('M', 'Cập nhật global_data')
dot.node('N', 'state_dim thay đổi?\nChuyển giao trọng số nếu cần')

# Kiểm tra user_id (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('O', 'User_id có trong\nuser_dict không?')

# Trả về phổ biến/ngẫu nhiên (màu đỏ nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('P', 'Trả về sản phẩm phổ biến\nhoặc ngẫu nhiên (top_k=200)')

# Tạo state và gợi ý (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('Q', 'Tạo state\n(user_id, 10 sản phẩm gần nhất,\ntổng điểm, tần suất, category,\nthời gian)')
dot.node('R', 'Kiểm tra lịch sử\ntrong state')
dot.node('S', 'Dự đoán Q-values\n(model.predict(state))')
dot.node('T', 'Kết hợp Q-values\nvới tổng điểm lịch sử')
dot.node('U', 'Loại bỏ sản phẩm\nbị remove_from_cart')
dot.node('V', 'Sắp xếp và trả về\nrecommendations (top_k=200)')

# API /update_policy (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('W', 'Nhận yêu cầu /update_policy\n(user_id, product_id,\naction_type, reward)')

# Kiểm tra thời gian cập nhật (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('X', 'Đã quá 60 giây\ntừ lần cập nhật cuối?')

# Cập nhật và kiểm tra state_dim (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('Y', 'Cập nhật global_data')
dot.node('Z', 'state_dim thay đổi?\nChuyển giao trọng số nếu cần')

# Kiểm tra dữ liệu hợp lệ (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('AA', 'Dữ liệu hợp lệ?')

# Báo lỗi (màu đỏ nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('AB', 'Báo lỗi: Dữ liệu không hợp lệ')

# Cập nhật SARSA (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('AC', 'Tạo state, next_state\n(user_id, lịch sử, new_product)')
dot.node('AD', 'Thêm vào replay_buffer\nvà huấn luyện nếu đủ batch')
dot.node('AE', 'Lưu mô hình\n(sarsa_model.keras)')

# Kết thúc (màu hồng nhạt, không viền cụm, căn giữa)
dot.attr('node', shape='ellipse', style='filled', fillcolor='lightpink')
dot.node('AF', 'Kết thúc', _attributes={'pos': '0,-30!'})  # Căn giữa dưới cùng

# Liên kết các nút
dot.edge('A', 'B')
dot.edge('B', 'C')
dot.edge('C', 'D')
dot.edge('D', 'E', label='Không')
dot.edge('D', 'F', label='Có')
dot.edge('F', 'G')
dot.edge('G', 'H', label='Không')
dot.edge('G', 'I', label='Có')
dot.edge('E', 'I')
dot.edge('H', 'I')
dot.edge('I', 'J')
dot.edge('J', 'K', style='dashed', label='API /recommend')
dot.edge('J', 'W', style='dashed', label='API /update_policy')
dot.edge('K', 'L')
dot.edge('L', 'M', label='Có')
dot.edge('L', 'O', label='Không')
dot.edge('M', 'N')
dot.edge('N', 'O')
dot.edge('O', 'P', label='Không')
dot.edge('O', 'Q', label='Có')
dot.edge('Q', 'R')
dot.edge('R', 'P', label='Không')
dot.edge('R', 'S', label='Có')
dot.edge('S', 'T')
dot.edge('T', 'U')
dot.edge('U', 'V')
dot.edge('W', 'X')
dot.edge('X', 'Y', label='Có')
dot.edge('X', 'AA', label='Không')
dot.edge('Y', 'Z')
dot.edge('Z', 'AA')
dot.edge('AA', 'AB', label='Không')
dot.edge('AA', 'AC', label='Có')
dot.edge('AC', 'AD')
dot.edge('AD', 'AE')

# Liên kết đến "Kết thúc" với nét đứt
dot.edge('P', 'AF', style='dotted', label='Hoàn tất /recommend\n(phổ biến/ngẫu nhiên)', constraint='true', weight='10')
dot.edge('V', 'AF', style='dotted', label='Hoàn tất /recommend\n(SARSA)', constraint='true', weight='10')
dot.edge('AB', 'AF', style='dotted', label='Hoàn tất lỗi\n/update_policy', constraint='true', weight='10')
dot.edge('AE', 'AF', style='dotted', label='Hoàn tất\n/update_policy', constraint='true', weight='10')

# Render lưu đồ
dot.render('sarsa_recommendation_flowchart', view=True)
print("Lưu đồ đã được tạo và lưu dưới dạng 'sarsa_recommendation_flowchart.png'")