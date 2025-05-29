import os
from graphviz import Digraph

# Thêm đường dẫn Graphviz vào PATH
os.environ["PATH"] += os.pathsep + 'C:/Users/quanc/Downloads/windows_10_cmake_Release_Graphviz-12.2.1-win64/Graphviz-12.2.1-win64/bin'

# Tạo đối tượng lưu đồ
dot = Digraph(comment='Actor-Critic Recommendation System Flowchart', format='png')
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
dot.node('C', 'Cập nhật global_data\n(user_ids, product_ids,\ncategory_ids, state_dim,\naction_dim)')

# Khởi tạo mô hình (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('D', 'Khởi tạo Actor-Critic\n(Actor: 128-64-softmax,\nCritic: 128-64-1,\nreplay_buffer=500)')

# Chuẩn bị dữ liệu huấn luyện (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('E', 'Chuẩn bị dữ liệu\n(state, action, reward,\nnext_state từ lịch sử)')

# Huấn luyện ban đầu (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('F', 'Huấn luyện Actor-Critic\n(100 epochs, batch_size=32,\nactor_loss, critic_loss)')
dot.node('G', 'Lưu mô hình\n(actor.keras, critic.keras)')

# API /recommend (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('H', 'Nhận yêu cầu /recommend\n(user_id, num_recommendations)')

# Kiểm tra user_id (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('I', 'User_id có trong\nuser_id_to_index không?')

# Trả về phổ biến/ngẫu nhiên (màu đỏ nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightcoral')
dot.node('J', 'Trả về sản phẩm phổ biến\nhoặc ngẫu nhiên')

# Load mô hình (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('K', 'Load mô hình\n(actor.keras, critic.keras)')

# Thu thập thông tin người dùng (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('L', 'Lấy lịch sử 10 hành động,\nignored_products, clicked_products,\ntop_categories')

# Kiểm tra lịch sử (màu vàng nhạt)
dot.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('M', 'Có lịch sử không?')

# Tạo state và gợi ý (màu xanh nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.node('N', 'Tạo state\n(user_id, product_scores,\ncategory_scores, thời gian)')
dot.node('O', 'Dự đoán action_probs\n(actor.predict(state))')
dot.node('P', 'Tính final_scores\n(prob, history, recent,\nrelated, penalty)')
dot.node('Q', 'Sắp xếp hoặc chọn ngẫu nhiên\n(epsilon=0.02)')
dot.node('R', 'Cập nhật replay_buffer\nvà huấn luyện nếu đủ dữ liệu')
dot.node('S', 'Trả về JSON\n(user_id, recommendations,\ntotal)')

# Background Training (màu xanh lá nhạt)
dot.attr('node', shape='box', style='filled', fillcolor='lightgreen')
dot.node('T', 'Background Training\n(cập nhật global_data,\nhuấn luyện mỗi 5 phút)')

# Kết thúc (màu hồng nhạt, không viền cụm, căn giữa)
dot.attr('node', shape='ellipse', style='filled', fillcolor='lightpink')
dot.node('U', 'Kết thúc', _attributes={'pos': '0,-30!'})  # Căn giữa dưới cùng

# Liên kết các nút
dot.edge('A', 'B')
dot.edge('B', 'C')
dot.edge('C', 'D')
dot.edge('D', 'E')
dot.edge('E', 'F')
dot.edge('F', 'G')
dot.edge('G', 'H', style='dashed', label='API /recommend')
dot.edge('G', 'T', style='dashed', label='Background Training')
dot.edge('H', 'I')
dot.edge('I', 'J', label='Không')
dot.edge('I', 'K', label='Có')
dot.edge('K', 'L')
dot.edge('L', 'M')
dot.edge('M', 'J', label='Không')
dot.edge('M', 'N', label='Có')
dot.edge('N', 'O')
dot.edge('O', 'P')
dot.edge('P', 'Q')
dot.edge('Q', 'R')
dot.edge('R', 'S')

# Liên kết đến "Kết thúc" với nét đứt
dot.edge('J', 'U', style='dotted', label='Hoàn tất /recommend\n(phổ biến/ngẫu nhiên)', constraint='true', weight='10')
dot.edge('S', 'U', style='dotted', label='Hoàn tất /recommend\n(Actor-Critic)', constraint='true', weight='10')
dot.edge('T', 'U', style='dotted', label='Hoàn tất\nbackground training', constraint='true', weight='10')

# Render lưu đồ
dot.render('actor_critic_recommendation_flowchart', view=True)
print("Lưu đồ đã được tạo và lưu dưới dạng 'actor_critic_recommendation_flowchart.png'")