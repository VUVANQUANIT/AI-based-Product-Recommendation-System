import os
from graphviz import Digraph

# Thêm đường dẫn Graphviz vào PATH (cập nhật theo máy của bạn)
os.environ["PATH"] += os.pathsep + 'C:/Users/quanc/Downloads/windows_10_cmake_Release_Graphviz-12.2.1-win64/Graphviz-12.2.1-win64/bin'

# Tạo đối tượng lưu đồ
dot = Digraph(comment='PPO Recommendation System Flowchart', format='png', engine='dot')
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
dot.node('C', 'Cập nhật global_state\n(user_dict, product_dict,\nstate_dim, action_dim)')

# Khởi tạo mô hình PPO (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('D', 'Khởi tạo PPOAgent\n(Actor: 128-128-softmax,\nCritic: 128-128-linear,\nbuffer_size=10000)')

# Kiểm tra mô hình cũ (màu vàng nhạt, hình thoi)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('E', 'Tồn tại mô hình cũ\n(ppo_actor.keras,\nppo_critic.keras)?')

# Load mô hình cũ (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('F', 'Load mô hình cũ\n(Chuyển giao nếu\nstate_dim/action_dim thay đổi)')

# Huấn luyện offline (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('G', 'Chuẩn bị dữ liệu offline\n(states, actions, rewards,\nvalues, log_probs)')
dot.node('H', 'Huấn luyện PPO offline\n(10 epochs, batch_size=64,\ngamma=0.95, clip_ratio=0.2)')
dot.node('I', 'Lưu mô hình\n(ppo_actor.keras,\nppo_critic.keras,\nppo_dims.json)')

# API /recommend (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('J', 'Nhận yêu cầu /recommend\n(user_id)')

# Kiểm tra user_id (màu vàng nhạt, hình thoi)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('K', 'User_id có trong\nuser_dict không?')

# Trả về rỗng (màu đỏ nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('L', 'Trả về JSON\n(recommendations rỗng)')

# Kiểm tra thời gian tải dữ liệu (màu vàng nhạt, hình thoi)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('M', 'Đã quá 3600 giây\nkể từ lần tải dữ liệu cuối?')

# Cập nhật dữ liệu toàn cục (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('N', 'Cập nhật global_state\nvà khởi tạo lại model\nnếu kích thước thay đổi')

# Tạo state (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('O', 'Tạo state\n(user_id, last_product_id,\nuser_history_len)')

# Dự đoán và gợi ý (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('P', 'Dự đoán action_probs\n(model.actor.predict(state))')
dot.node('Q', 'Sắp xếp action_probs\nvà chọn top 50 sản phẩm')

# Trả về kết quả (màu xanh nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('R', 'Trả về JSON\n(user_id, recommendations)')

# API /update_policy (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('S', 'Nhận yêu cầu /update_policy\n(user_id, product_id, reward)')

# Kiểm tra user_id và product_id (màu vàng nhạt, hình thoi)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('T', 'User_id và product_id\ncó trong dữ liệu không?')

# Trả về lỗi (màu đỏ nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('U', 'Trả về lỗi\n(user/sản phẩm không tồn tại)')

# Cập nhật buffer và huấn luyện (màu xanh lá nhạt, hình hộp)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('V', 'Tạo state và lưu vào\nonline_buffer\n(state, action, reward,\nvalue, log_prob)')
dot.node('W', 'Kiểm tra đủ số mẫu\nhoặc đạt train_interval?')
dot.node('X', 'Huấn luyện PPO online\n(10 epochs, batch_size=64)')
dot.node('Y', 'Lưu mô hình nếu\nđạt save_interval')

# Kết thúc (màu hồng nhạt, hình elip)
dot.attr('node', shape='ellipse', style='filled', fillcolor='lightpink')
dot.node('Z', 'Kết thúc')

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
dot.edge('I', 'S', style='dashed', label='API /update_policy')
dot.edge('J', 'K')
dot.edge('K', 'L', label='Không')
dot.edge('K', 'M', label='Có')
dot.edge('M', 'N', label='Có')
dot.edge('M', 'O', label='Không')
dot.edge('N', 'O')
dot.edge('O', 'P')
dot.edge('P', 'Q')
dot.edge('Q', 'R')
dot.edge('R', 'Z', style='dotted', label='Hoàn tất /recommend')
dot.edge('L', 'Z', style='dotted', label='Hoàn tất /recommend (rỗng)')
dot.edge('S', 'T')
dot.edge('T', 'U', label='Không')
dot.edge('T', 'V', label='Có')
dot.edge('V', 'W')
dot.edge('W', 'X', label='Có')
dot.edge('W', 'Z', style='dotted', label='Không')  # Sửa lỗi: chỉ giữ nhãn "Không"
dot.edge('X', 'Y')
dot.edge('Y', 'Z', style='dotted', label='Hoàn tất /update_policy')
dot.edge('U', 'Z', style='dotted', label='Hoàn tất /update_policy (lỗi)')

# Render lưu đồ
dot.render('ppo_recommendation_flowchart', view=True)
print("Lưu đồ đã được tạo và lưu dưới dạng 'ppo_recommendation_flowchart.png'")