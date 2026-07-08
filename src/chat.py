import os
import google.generativeai as genai
from dotenv import load_dotenv

# Tải cấu hình từ file .env
load_dotenv()

# Cấu hình API Key cho Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Không tìm thấy GEMINI_API_KEY trong file .env. Vui lòng cấu hình lại!")

genai.configure(api_key=api_key)

def init_chat_session():
    """
    Khởi tạo phiên trò chuyện với mô hình Gemini
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    return chat

def send_message_to_bot(chat_session, user_message):
    """
    Gửi tin nhắn của người dùng đến Bot và nhận phản hồi
    """
    try:
        response = chat_session.send_message(user_message)
        return response.text
    except Exception as e:
        return f"Đã xảy ra lỗi khi kết nối với Gemini AI: {str(e)}"

if __name__ == "__main__":
    print("--- Khởi động NebulaBot Assistant ---")
    chat = init_chat_session()
    print("Bot đã sẵn sàng! Gõ 'exit' hoặc 'quit' để thoát.\n")
    
    while True:
        user_input = input("Bạn: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Tạm biệt!")
            break
            
        if not user_input.strip():
            continue
            
        bot_response = send_message_to_bot(chat, user_input)
        print(f"Bot: {bot_response}\n")