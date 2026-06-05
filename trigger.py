import requests

# ==========================================
# CẤU HÌNH THÔNG TIN CỦA BẠN TẠI ĐÂY
# ==========================================
# Địa chỉ gốc của Teacher Server (theo slide)
TEACHER_BASE_URL = "http://192.168.50.218:8000/api/v1"

# Mã sinh viên của bạn (BẮT BUỘC VIẾT HOA)
STUDENT_ID = "B22DCAT149" # Nhớ sửa thành MSSV của bạn

# Địa chỉ Student Server của bạn chạy ở local 
# (Dùng IP LAN lấy từ lệnh ipconfig, KHÔNG dùng localhost hay 0.0.0.0)
STUDENT_SERVER_URL = "http://192.168.50.67:5000" 
# ==========================================

# Header dùng chung cho mọi request để định danh sinh viên
HEADERS = {
    "X-Student-ID": STUDENT_ID
}

def register():
    """
    POST /competition/register
    Đăng ký địa chỉ Student Server với Teacher Server.
    """
    print(">>> Đang gửi yêu cầu ĐĂNG KÝ (Register)...")
    url = f"{TEACHER_BASE_URL}/competition/register"
    payload = {
        "server_url": STUDENT_SERVER_URL
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
        return response.status_code == 200
    except Exception as e:
        print(f"Lỗi kết nối: {e}\n")
        return False

def evaluate():
    """
    POST /competition/evaluate
    Kích hoạt Teacher Server bắt đầu quá trình gửi document và câu hỏi.
    """
    print(">>> Đang gửi yêu cầu BẮT ĐẦU THI (Evaluate)...")
    url = f"{TEACHER_BASE_URL}/competition/evaluate"
    
    try:
        # Endpoint này không cần Content Body (json)
        response = requests.post(url, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"Lỗi kết nối: {e}\n")

def reset():
    """
    POST /competition/reset
    Xóa điểm cũ, reset trạng thái thi để làm lại từ đầu (dùng khi code bị crash).
    """
    print(">>> Đang gửi yêu cầu LÀM LẠI TỪ ĐẦU (Reset)...")
    url = f"{TEACHER_BASE_URL}/competition/reset"
    
    try:
        response = requests.post(url, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"Lỗi kết nối: {e}\n")

def get_result():
    """
    GET /competition/result
    Kiểm tra trạng thái thi và điểm số hiện tại.
    """
    print(">>> Đang lấy KẾT QUẢ HIỆN TẠI (Result)...")
    url = f"{TEACHER_BASE_URL}/competition/result"
    
    try:
        # Lưu ý đây là method GET
        response = requests.get(url, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"Lỗi kết nối: {e}\n")

# ==========================================
# KHU VỰC THỰC THI CHÍNH (MAIN ENTRY)
# ==========================================
if __name__ == "__main__":
    print(f"--- TOOL ĐIỀU KHIỂN RAG COMPETITION - MSSV: {STUDENT_ID} ---")
    
    # Kịch bản 1: Lần đầu tiên chạy
    # Uncomment 2 dòng dưới để chạy đăng ký và kích hoạt thi
    
    # is_registered = register()
    # if is_registered:
    #     evaluate()
    
    # -------------------------------------------------------------
    # Kịch bản 2: Muốn xem điểm số hoặc trạng thái lúc đang thi
    # Chỉ cần chạy dòng dưới đây:
    
    # get_result()
    
    # -------------------------------------------------------------
    # Kịch bản 3: Code server của bạn bị sập, muốn làm lại từ đầu
    # Chạy lần lượt Reset -> Đăng ký lại -> Evaluate
    
    # reset()
    register()
    evaluate()