import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Tải cấu hình từ file .env bảo mật
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Không tìm thấy GEMINI_API_KEY trong file .env!")

# Khởi tạo Client Gemini API
client = genai.Client(api_key=GEMINI_API_KEY)
STORE_DISPLAY_NAME = "OptiSigns-Knowledge-Base"

def get_or_create_vector_store():
    """Kiểm tra xem kho dữ liệu vector đã tồn tại chưa, nếu chưa thì tạo mới."""
    try:
        # Liệt kê các store hiện có trên tài khoản
        for store in client.file_search_stores.list():
            if store.display_name == STORE_DISPLAY_NAME:
                print(f"📦 Đã tìm thấy Kho lưu trữ Vector hiện có: {store.name}")
                return store
    except Exception as e:
        print(f"⚠️ Không thể liệt kê store cũ, tiến hành tạo mới: {e}")

    print(f"✨ Đang khởi tạo Kho lưu trữ Vector mới: {STORE_DISPLAY_NAME}...")
    # Khởi tạo store sử dụng mô hình embedding thế hệ 2 mới nhất của Google
    new_store = client.file_search_stores.create(
        config={
            "display_name": STORE_DISPLAY_NAME,
            "embedding_model": "models/gemini-embedding-2"
        }
    )
    print(f"✅ Đã tạo thành công Vector Store: {new_store.name}")
    return new_store

def upload_markdown_files(data_dir="data"):
    """Duyệt qua các file Markdown trong thư mục data và nạp vào Vector Store bằng API."""
    if not os.path.exists(data_dir):
        print(f"❌ Thư mục '{data_dir}' không tồn tại. Vui lòng chạy scraper trước.")
        return

    vector_store = get_or_create_vector_store()
    
    # Lấy danh sách tất cả file .md trong thư mục data
    files = [f for f in os.listdir(data_dir) if f.endswith(".md")]
    print(f"📂 Tìm thấy {len(files)} file chuẩn bị tải lên.")

    uploaded_count = 0
    
    for index, file_name in enumerate(files, 1):
        file_path = os.path.join(data_dir, file_name)
        print(f"🔄 [{index}/{len(files)}] Đang tải lên bằng API: {file_name}")
        
        try:
            # Thực hiện đồng thời việc Upload file và Import nó thẳng vào kho lưu trữ Vector của Google
            operation = client.file_search_stores.upload_to_file_search_store(
                file_search_store_name=vector_store.name,
                file=file_path,
                config={"display_name": file_name}
            )
            
            # Đợi cho hệ thống của Google xử lý băm và nhúng vector (Embedding) hoàn tất
            while not operation.done:
                print("   ⌛ Đang xử lý tính toán embedding dữ liệu...")
                time.sleep(3)
                # Cập nhật trạng thái của tiến trình (Polling)
                operation = client.operations.get(operation=operation)
                
            uploaded_count += 1
            print(f"   ✅ Đã nhúng vector thành công cho file: {file_name}")
            
        except Exception as e:
            print(f"   ❌ Lỗi khi xử lý file {file_name}: {e}")
            continue

    print(f"🎉 Hoàn thành! Đã nạp thành công {uploaded_count} file dữ liệu vào Vector Store.")

if __name__ == "__main__":
    upload_markdown_files()