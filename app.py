import streamlit as st
from google import genai
import random
import urllib.parse 

# ==========================================
# 1. CẤU HÌNH API KEY CỦA BẠN VÀO ĐÂY
# ==========================================
GOOGLE_API_KEY = "AIzaSyDU2Wz9SwaxzhGMxLey0wHG-MGncl_zCZ0"
client = genai.Client(api_key=GOOGLE_API_KEY)

# ==========================================
# 2. CHUẨN BỊ DỮ LIỆU: ĐẦY ĐỦ 78 LÁ BÀI
# ==========================================
TAROT_DECK = [
    # --- Major Arcana (22 lá Ẩn chính) ---
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
    
    # --- Minor Arcana: Wands - Bộ Gậy (14 lá) ---
    "Ace of Wands", "Two of Wands", "Three of Wands", "Four of Wands", "Five of Wands",
    "Six of Wands", "Seven of Wands", "Eight of Wands", "Nine of Wands", "Ten of Wands",
    "Page of Wands", "Knight of Wands", "Queen of Wands", "King of Wands",
    
    # --- Minor Arcana: Cups - Bộ Cốc (14 lá) ---
    "Ace of Cups", "Two of Cups", "Three of Cups", "Four of Cups", "Five of Cups",
    "Six of Cups", "Seven of Cups", "Eight of Cups", "Nine of Cups", "Ten of Cups",
    "Page of Cups", "Knight of Cups", "Queen of Cups", "King of Cups",
    
    # --- Minor Arcana: Swords - Bộ Kiếm (14 lá) ---
    "Ace of Swords", "Two of Swords", "Three of Swords", "Four of Swords", "Five of Swords",
    "Six of Swords", "Seven of Swords", "Eight of Swords", "Nine of Swords", "Ten of Swords",
    "Page of Swords", "Knight of Swords", "Queen of Swords", "King of Swords",
    
    # --- Minor Arcana: Pentacles - Bộ Tiền (14 lá) ---
    "Ace of Pentacles", "Two of Pentacles", "Three of Pentacles", "Four of Pentacles", "Five of Pentacles",
    "Six of Pentacles", "Seven of Pentacles", "Eight of Pentacles", "Nine of Pentacles", "Ten of Pentacles",
    "Page of Pentacles", "Knight of Pentacles", "Queen of Pentacles", "King of Pentacles"
]

# ==========================================
# 3. GIAO DIỆN NGƯỜI DÙNG
# ==========================================
st.set_page_config(page_title="Mystic Vision Tarot", page_icon="🔮", layout="wide")
st.title("🔮 Hệ Thống Bói Tarot: Mystic Vision (Bản Đầy Đủ)")
st.write("Bộ bài 78 lá đã sẵn sàng. Hãy tập trung vào vấn đề của bạn và đặt câu hỏi.")

user_question = st.text_input("Câu hỏi của bạn (VD: Tình hình công việc của tôi tháng tới sẽ ra sao?):")

if st.button("Trộn Bài & Rút 3 Lá"):
    if not user_question:
        st.warning("Bạn phải nhập câu hỏi trước khi rút bài nhé!")
    else:
        with st.spinner('Đang kết nối với năng lượng vũ trụ...'):
            # --- RÚT BÀI VÀ XÁC ĐỊNH CHIỀU XUÔI/NGƯỢC ---
            drawn_cards_raw = random.sample(TAROT_DECK, 3)
            drawn_cards = []
            
            # Tỉ lệ 50% xuất hiện bài ngược
            for card in drawn_cards_raw:
                is_reversed = random.choice([True, False])
                if is_reversed:
                    drawn_cards.append(f"{card} (Ngược)")
                else:
                    drawn_cards.append(f"{card} (Xuôi)")
                    
            cards_text = f"1. {drawn_cards[0]} | 2. {drawn_cards[1]} | 3. {drawn_cards[2]}"
            
            # --- CÂU LỆNH CHO GEMINI (PROMPT) ---
            system_prompt = f"""
            Bạn là một Master Tarot tên là Mystic Vision. 
            Người dùng vừa hỏi: '{user_question}'
            Họ bốc được 3 lá bài theo thứ tự Quá Khứ - Hiện Tại - Tương Lai là: 
            1. {drawn_cards[0]}
            2. {drawn_cards[1]}
            3. {drawn_cards[2]}
            
            Chú ý: Nếu lá bài có chữ (Ngược), hãy giải thích ý nghĩa đảo ngược của nó.
            Hãy giải nghĩa thật sâu sắc, rành mạch từng lá bài, phân tích sự liên kết giữa chúng 
            và đưa ra lời khuyên tổng kết. Văn phong bí ẩn, thấu cảm và truyền cảm hứng.
            """
            
            try:
                # --- 1. GỌI GEMINI ĐỂ GIẢI BÀI ---
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=system_prompt
                )
                interpretation = response.text
                
                # --- 2. TẠO ẢNH BẰNG POLLINATIONS AI ---
                # Chúng ta dùng tên tiếng Anh gốc (không kèm chữ xuôi/ngược) để AI vẽ hình chuẩn xác hơn
                image_prompt = f"Digital fantasy art, tarot card style, mystical scene combining {drawn_cards_raw[0]}, {drawn_cards_raw[1]}, {drawn_cards_raw[2]}. Highly detailed, cinematic lighting, masterpiece."
                
                encoded_prompt = urllib.parse.quote(image_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=450&nologo=true"
                
                # --- 3. HIỂN THỊ KẾT QUẢ ---
                st.success(f"Đã rút thành công: {cards_text}")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("Tầm Nhìn Trực Quan")
                    st.image(image_url, caption="Hình ảnh tổng hợp năng lượng trải bài của bạn", use_container_width=True)
                
                with col2:
                    st.subheader("Thông Điệp Từ Vũ Trụ")
                    st.write(interpretation)

            except Exception as e:
                st.error(f"Có lỗi xảy ra khi kết nối vũ trụ: {e}")