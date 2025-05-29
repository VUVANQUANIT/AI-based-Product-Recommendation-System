import os
from graphviz import Digraph

# Thêm đường dẫn Graphviz vào PATH
os.environ["PATH"] += os.pathsep + 'C:/Users/quanc/Downloads/windows_10_cmake_Release_Graphviz-12.2.1-win64/Graphviz-12.2.1-win64/bin'

dot = Digraph(comment='Decision Making Model', format='png')

# Thiết lập hướng ngang và font tổng thể
dot.attr(rankdir='LR', splines='ortho', bgcolor='white', fontname='Arial')

# Thêm các node với kiểu dáng
dot.node('U', 'Người dùng\n(User)', shape='ellipse', style='filled', fillcolor='#E6F3FF', color='#0066CC', fontcolor='#003366', fontsize='12')
dot.node('W', 'Web\n(Frontend)', shape='box', style='filled,rounded', fillcolor='#E6FFE6', color='#009900', fontcolor='#003300', fontsize='12')
dot.node('B', 'Backend\n(Xử lý hành vi)', shape='box', style='filled,rounded', fillcolor='#FFE6E6', color='#CC0000', fontcolor='#330000', fontsize='12')
dot.node('D', 'Cơ sở dữ liệu\n(Database)', shape='cylinder', style='filled', fillcolor='#FFFFCC', color='#FF9900', fontcolor='#663300', fontsize='12')
dot.node('O', 'Kết quả\n(Sản phẩm gợi ý)', shape='ellipse', style='filled', fillcolor='#E6F3FF', color='#0066CC', fontcolor='#003366', fontsize='12')

# Thêm các cạnh với nhãn
dot.edge('U', 'W', label='Tương tác\n(Gửi yêu cầu)', color='#0066CC', fontcolor='#003366', fontsize='10')
dot.edge('W', 'B', label='Chuyển hành vi', color='#009900', fontcolor='#003300', fontsize='10')
dot.edge('B', 'D', label='Truy vấn dữ liệu', color='#CC0000', fontcolor='#330000', fontsize='10')
dot.edge('D', 'B', label='Trả về dữ liệu', color='#FF9900', fontcolor='#663300', fontsize='10')
dot.edge('B', 'W', label='Gửi gợi ý', color='#009900', fontcolor='#003300', fontsize='10')
dot.edge('W', 'O', label='Hiển thị sản phẩm', color='#0066CC', fontcolor='#003366', fontsize='10')
dot.edge('O', 'U', label='Nhận gợi ý', color='#0066CC', fontcolor='#003366', fontsize='10')

# Điều chỉnh bố cục để tránh rời rạc
dot.attr('node', rank='same')
dot.attr('edge', minlen='2')  # Tăng khoảng cách giữa các node để dễ nhìn
dot.node('U', rank='source')  # Đặt Người dùng ở đầu luồng
dot.node('O', rank='sink')    # Đặt Kết quả ở cuối luồng

# Lưu và xuất file sơ đồ
dot.render('decision_model_diagram', view=True)  # Xuất file PNG và mở xem
dot.render('decision_model_diagram', format='png')  # Xuất file PNG mà không mở xem   