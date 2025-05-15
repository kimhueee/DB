import matplotlib.pyplot as plt

# Dữ liệu: số lượng đơn hàng theo ngày
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
orders = [20, 35, 30, 25, 40]

# Vẽ biểu đồ đường
plt.plot(days, orders, marker='o', linestyle='-', color='green')

# Thêm tiêu đề và nhãn trục
plt.title('Số lượng đơn hàng trong tuần')
plt.xlabel('Ngày')
plt.ylabel('Số đơn hàng')

# Hiển thị biểu đồ
plt.show()

# Vẽ biểu đồ cột
plt.bar(days, orders, color='orange')

# Thêm tiêu đề và nhãn trục
plt.title('Số lượng đơn hàng trong tuần (Bar chart)')
plt.xlabel('Ngày')
plt.ylabel('Số đơn hàng')

# Hiển thị biểu đồ
plt.show()

