
import json
import os
import hashlib
import hmac
import secrets

DATA_FILE = "users.json"


def load_users():
    """Đọc danh sách user từ file JSON."""
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}

#cwe
def save_users(users):
    """Lưu danh sách user vào file JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)


def hash_password(password, salt=None):
    """Băm mật khẩu bằng PBKDF2."""
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        600_000
    ).hex()

    return salt, password_hash


def register():
    """Đăng ký tài khoản mới."""
    users = load_users()

    username = input("Nhập username: ").strip()
    password = input("Nhập password: ")

    if not username or not password:
        print("Username và password không được để trống.")
        return

    if username in users:
        print("Username đã tồn tại.")
        return

    if len(password) < 8:
        print("Password phải có ít nhất 8 ký tự.")
        return

    salt, password_hash = hash_password(password)

    users[username] = {
        "salt": salt,
        "password_hash": password_hash
    }

    save_users(users)
    print("Đăng ký thành công!")


def login():
    """Đăng nhập bằng username và password."""
    users = load_users()

    username = input("Nhập username: ").strip()
    password = input("Nhập password: ")

    user = users.get(username)

    if user is None:
        print("Username hoặc password không chính xác.")
        return False

    salt = user["salt"]
    expected_hash = user["password_hash"]

    _, actual_hash = hash_password(password, salt)

    if hmac.compare_digest(actual_hash, expected_hash):
        print(f"Đăng nhập thành công! Xin chào {username}.")
        return True

    print("Username hoặc password không chính xác.")
    return False


def main():
    while True:
        print("\n===== USER AUTHENTICATION =====")
        print("1. Đăng ký")
        print("2. Đăng nhập")
        print("3. Thoát")

        choice = input("Chọn chức năng: ").strip()

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Đã thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()
