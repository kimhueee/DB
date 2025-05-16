import streamlit as st
import matplotlib.pyplot as plt

# Tiêu đề trang
st.title("Biểu đồ đơn hàng theo ngày")

# Dữ liệu: số lượng đơn hàng theo ngày
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
orders = [120, 150, 90, 170, 200]

# Tạo biểu đồ bằng matplotlib
fig, ax = plt.subplots()
ax.plot(days, orders, marker='o', linestyle='-', color='blue')

# Thêm nhãn cho trục và tiêu đề biểu đồ
ax.set_xlabel("Thứ trong tuần")
ax.set_ylabel("Số đơn hàng")
ax.set_title("Số lượng đơn hàng theo ngày")

# Hiển thị biểu đồ trong Streamlit
st.pyplot(fig)