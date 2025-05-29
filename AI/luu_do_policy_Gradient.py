import os
from graphviz import Digraph

# Thêm đường dẫn Graphviz vào PATH
os.environ["PATH"] += os.pathsep + 'C:/Users/quanc/Downloads/windows_10_cmake_Release_Graphviz-12.2.1-win64/Graphviz-12.2.1-win64/bin'

# Tạo đối tượng lưu đồ
dot = Digraph(comment='Policy Gradient Recommendation System Flowchart', format='png')
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
dot.node('D', 'Mô hình Policy Gradient\nđã tồn tại?')

# Khởi tạo mô hình (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('E', 'Khởi tạo mô hình Policy Gradient\n(state_dim, action_dim,\n128-128-softmax)')

# Load mô hình (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('F', 'Load mô hình\ntừ policy_model.keras')

# Kiểm tra kích thước mô hình (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('G', 'Kích thước mô hình\nkhớp với global_data?')

# Huấn luyện ban đầu (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('H', 'Huấn luyện Policy Gradient\n(episodes=20, history_length=5,\nreplay_buffer, train(states, actions, rewards))')
dot.node('I', 'Lưu mô hình\n(policy_model.keras)')

# API /recommend (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('J', 'Nhận yêu cầu /recommend\n(user_id từ request)')

# Kiểm tra user_id (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('K', 'User_id có trong\nuser_dict không?')

# Trả về phổ biến/ngẫu nhiên (màu đỏ nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('L', 'Trả về sản phẩm phổ biến\nhoặc ngẫu nhiên (top_k=40)')

# Tạo state và gợi ý (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('M', 'Tạo state\n(user_id, 5 sản phẩm gần nhất,\nscore, category, thời gian)')
dot.node('N', 'Dự đoán xác suất\n(model.predict(state))')
dot.node('O', 'Kết hợp xác suất\nvới điểm lịch sử')
dot.node('P', 'Loại bỏ sản phẩm\nbị remove_from_cart')
dot.node('Q', 'Sắp xếp và thêm\nsản phẩm ngẫu nhiên (20%)')
dot.node('R', 'Trả về JSON\n(user_id, recommendations)')

# API /update_policy (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('S', 'Nhận yêu cầu /update_policy\n(user_id, product_id,\naction_type, reward)')

# Kiểm tra dữ liệu hợp lệ (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('T', 'Dữ liệu hợp lệ?')

# Báo lỗi (màu đỏ nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('U', 'Báo lỗi: Dữ liệu không hợp lệ')

# Cập nhật chính sách (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('V', 'Thêm dữ liệu vào MySQL\n(user_behavior)')
dot.node('W', 'Tạo state\n(user_id, 5 sản phẩm gần nhất)')
dot.node('X', 'Huấn luyện Policy Gradient\n(train(state, action, reward))')
dot.node('Y', 'Lưu mô hình\n(policy_model.keras)')

# Background training (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('Z', 'Background Training\n(cập nhật global_data,\nhuấn luyện mỗi 5 phút)')

# Kết thúc (màu hồng nhạt, không viền cụm, căn giữa)
dot.attr('node', shape='ellipse', style='filled', fillcolor='lightpink')
dot.node('AA', 'Kết thúc', _attributes={'pos': '0,-30!'})  # Căn giữa dưới cùng

# Liên kết các nút
dot.edge('A', 'B')
dot.edge('B', 'C')
dot.edge('C', 'D')
dot.edge('D', 'E', label='Không')
dot.edge('D', 'F', label='Có')
dot.edge('F', 'G')
dot.edge('G', 'E', label='Không')
dot.edge('G', 'H', label='Có')
dot.edge('E', 'H')
dot.edge('H', 'I')
dot.edge('I', 'J', style='dashed', label='API /recommend')
dot.edge('I', 'S', style='dashed', label='API /update_policy')
dot.edge('I', 'Z', style='dashed', label='Background Training')
dot.edge('J', 'K')
dot.edge('K', 'L', label='Không')
dot.edge('K', 'M', label='Có')
dot.edge('M', 'N')
dot.edge('N', 'O')
dot.edge('O', 'P')
dot.edge('P', 'Q')
dot.edge('Q', 'R')
dot.edge('S', 'T')
dot.edge('T', 'U', label='Không')
dot.edge('T', 'V', label='Có')
dot.edge('V', 'W')
dot.edge('W', 'X')
dot.edge('X', 'Y')

# Liên kết đến "Kết thúc" với nét đứt
dot.edge('L', 'AA', style='dotted', label='Hoàn tất /recommend\n(phổ biến/ngẫu nhiên)', constraint='true', weight='10')
dot.edge('R', 'AA', style='dotted', label='Hoàn tất /recommend\n(Policy Gradient)', constraint='true', weight='10')
dot.edge('U', 'AA', style='dotted', label='Hoàn tất lỗi\n/update_policy', constraint='true', weight='10')
dot.edge('Y', 'AA', style='dotted', label='Hoàn tất\n/update_policy', constraint='true', weight='10')
dot.edge('Z', 'AA', style='dotted', label='Hoàn tất\nbackground training', constraint='true', weight='10')

# Render lưu đồ
dot.render('policy_gradient_recommendation_flowchart', view=True)
print("Lưu đồ đã được tạo và lưu dưới dạng 'policy_gradient_recommendation_flowchart.png'")