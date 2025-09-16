import random

def random_game():
    secret_number = random.randint(1, 12)  # số bí mật
    players = int(input("Nhập số lượng người chơi: "))
    used_numbers = set()
    winners = []

    print("\n🎲 Welcome to Random Game!")
    print("Mỗi người chơi nhập TÊN và chọn 1 số từ 1 đến 12 (không được trùng).")
    print("Ai chọn trúng số bí mật sẽ chiến thắng!\n")

    player_choices = {}  # lưu tên + số

    for i in range(1, players + 1):
        while True:
            try:
                name = input(f"👤 Nhập tên người chơi {i}: ").strip()
                number = int(input(f"👉 {name}, chọn số của bạn (1-12): "))

                # kiểm tra số hợp lệ
                if number < 1 or number > 12:
                    print("⚠️ Vui lòng nhập số trong khoảng 1-12!")
                    continue

                # kiểm tra trùng số
                if number in used_numbers:
                    print("⚠️ Số này đã có người chọn, hãy chọn số khác!")
                    continue

                # lưu số đã chọn
                used_numbers.add(number)
                player_choices[name] = number

                # kiểm tra thắng
                if number == secret_number:
                    winners.append(name)

                break  # kết thúc lượt người chơi này

            except ValueError:
                print("⚠️ Bạn phải nhập số nguyên hợp lệ!")

    # công bố kết quả
    print("\n===== 🎉 KẾT QUẢ 🎉 =====")
    print(f"Số bí mật là: {secret_number}")
    print("Danh sách chọn số:")
    for name, number in player_choices.items():
        print(f" - {name}: {number}")

    if winners:
        print("\n🏆 Người chiến thắng:", ", ".join(winners))
    else:
        print("\n😢 Không ai đoán đúng!")

# chạy game
random_game()