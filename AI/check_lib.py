from graphviz import Digraph
import os

os.environ["PATH"] += os.pathsep + 'C:/Users/quanc/Downloads/windows_10_cmake_Release_Graphviz-12.2.1-win64/Graphviz-12.2.1-win64/bin'


dot = Digraph(comment='Recommendation Algorithm Flowchart')
dot.attr(rankdir='TB', size='12,18')  # Top to Bottom layout, tăng kích thước

# Định nghĩa màu sắc
colors = {
    'start_end': '#FF9999',  # Đỏ nhạt cho bắt đầu/kết thúc
    'process': '#99CCFF',    # Xanh dương nhạt cho quá trình
    'decision': '#FFFF99',   # Vàng nhạt cho quyết định
    'error': '#FFCC99'       # Cam nhạt cho lỗi
}

# Thêm các nút với màu sắc
dot.node('A', 'Bắt đầu', shape='oval', style='filled', fillcolor=colors['start_end'])
dot.node('B', 'Nhận user_id và num_recommendations từ request', shape='box', style='filled', fillcolor=colors['process'])
dot.node('C', 'Kết nối database', shape='box', style='filled', fillcolor=colors['process'])
dot.node('D', 'User_id có trong dữ liệu không?', shape='diamond', style='filled', fillcolor=colors['decision'])
dot.node('E', 'Load mô hình Actor-Critic', shape='box', style='filled', fillcolor=colors['process'])
dot.node('F', 'Lấy lịch sử 10 hành động gần nhất của user', shape='box', style='filled', fillcolor=colors['process'])
dot.node('G', 'Lấy danh sách sản phẩm bị bỏ qua và đã click', shape='box', style='filled', fillcolor=colors['process'])
dot.node('H', 'Lấy 3 danh mục phổ biến của user', shape='box', style='filled', fillcolor=colors['process'])
dot.node('I', 'Tạo state vector từ user_id, lịch sử, thời gian', shape='box', style='filled', fillcolor=colors['process'])
dot.node('J', 'Dự đoán xác suất hành động bằng Actor', shape='box', style='filled', fillcolor=colors['process'])
dot.node('K', 'Lịch sử có rỗng không?', shape='diamond', style='filled', fillcolor=colors['decision'])
dot.node('L', 'Tính điểm cuối cùng cho mỗi sản phẩm\n(prob + history + recent + category + penalty)', shape='box', style='filled', fillcolor=colors['process'])
dot.node('M', 'Random < epsilon?', shape='diamond', style='filled', fillcolor=colors['decision'])
dot.node('N', 'Sắp xếp sản phẩm theo điểm\nLoại bỏ sản phẩm bị bỏ qua', shape='box', style='filled', fillcolor=colors['process'])
dot.node('O', 'Chọn ngẫu nhiên sản phẩm', shape='box', style='filled', fillcolor=colors['process'])
dot.node('P', 'Cập nhật vị trí sản phẩm gần nhất\n nếu có hành động', shape='box', style='filled', fillcolor=colors['process'])
dot.node('Q', 'Trả về danh sách gợi ý', shape='box', style='filled', fillcolor=colors['process'])
dot.node('R', 'Kết thúc', shape='oval', style='filled', fillcolor=colors['start_end'])
dot.node('S', 'Lấy sản phẩm phổ biến nhất từ DB', shape='box', style='filled', fillcolor=colors['process'])
dot.node('T', 'Cập nhật replay buffer và train nếu đủ dữ liệu', shape='box', style='filled', fillcolor=colors['process'])
dot.node('U', 'Xử lý lỗi', shape='box', style='filled', fillcolor=colors['error'])

# Liên kết các nút
dot.edge('A', 'B')
dot.edge('B', 'C')
dot.edge('C', 'D')
dot.edge('D', 'E', label='Có')
dot.edge('D', 'S', label='Không')
dot.edge('E', 'F')
dot.edge('F', 'G')
dot.edge('G', 'H')
dot.edge('H', 'I')
dot.edge('I', 'J')
dot.edge('J', 'K')
dot.edge('K', 'L', label='Không')
dot.edge('K', 'S', label='Có')
dot.edge('L', 'M')
dot.edge('M', 'N', label='Không')
dot.edge('M', 'O', label='Có')
dot.edge('N', 'P')
dot.edge('O', 'P')
dot.edge('P', 'T')
dot.edge('T', 'Q')
dot.edge('S', 'Q')
dot.edge('Q', 'R')
dot.edge('C', 'U', label='Lỗi')
dot.edge('E', 'U', label='Lỗi')
dot.edge('F', 'U', label='Lỗi')
dot.edge('S', 'U', label='Lỗi')

# Đặt "Bắt đầu" ở giữa bằng cách điều chỉnh rank
with dot.subgraph() as s:
    s.attr(rank='source')
    s.node('A')

# Lưu và hiển thị lưu đồ
dot.render('recommendation_flowchart_colored', format='png', view=True)