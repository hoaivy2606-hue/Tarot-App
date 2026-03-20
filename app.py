import streamlit as st
from google import genai
import random
import urllib.parse
import time # Thêm thư viện để tạo hiệu ứng chờ
from PIL import Image
import requests
from io import BytesIO

# ==========================================
# 1. CẤU HÌNH API KEY (DÙNG STREAMLIT SECRETS)
# ==========================================
# Khuyến khích: Sử dụng st.secrets để bảo mật.
# Nếu bạn deploy lên Streamlit Cloud, hãy vào phần settings -> Secrets và dán:
# [secrets]
# GOOGLE_API_KEY = "GOOGLE_API_KEY = "DUNG_DANG_API_KEY_THAT_VAO_DAY""
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Nếu chạy local mà chưa có secrets, bạn có thể điền tạm vào đây
    # NHƯNG ĐỪNG COMMIT NÓ LÊN GITHUB
    GOOGLE_API_KEY = "ĐIỀN_TẠM_MÃ_API_VÀO_ĐÂY_ĐỂ_CHẠY_LOCAL"

client = genai.Client(api_key=GOOGLE_API_KEY)

# ==========================================
# 2. CHUẨN BỊ DỮ LIỆU: ĐẦY ĐỦ 78 LÁ BÀI
# ==========================================
TAROT_DECK = [
    # Major Arcana
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
    # Minor Arcana
    "Ace of Wands", "Two of Wands", "Three of Wands", "Four of Wands", "Five of Wands",
    "Six of Wands", "Seven of Wands", "Eight of Wands", "Nine of Wands", "Ten of Wands",
    "Page of Wands", "Knight of Wands", "Queen of Wands", "King of Wands",
    "Ace of Cups", "Two of Cups", "Three of Cups", "Four of Cups", "Five of Cups",
    "Six of Cups", "Seven of Cups", "Eight of Cups", "Nine of Cups", "Ten of Cups",
    "Page of Cups", "Knight of Cups", "Queen of Cups", "King of Cups",
    "Ace of Swords", "Two of Swords", "Three of Swords", "Four of Swords", "Five of Swords",
    "Six of Swords", "Seven of Swords", "Eight of Swords", "Nine of Swords", "Ten of Swords",
    "Page of Swords", "Knight of Swords", "Queen of Swords", "King of Swords",
    "Ace of Pentacles", "Two of Pentacles", "Three of Pentacles", "Four of Pentacles", "Five of Pentacles",
    "Six of Pentacles", "Seven of Pentacles", "Eight of Pentacles", "Nine of Pentacles", "Ten of Pentacles",
    "Page of Pentacles", "Knight of Pentacles", "Queen of Pentacles", "King of Pentacles"
]

# Link ảnh GIF trộn bài công khai
SHUFFLING_GIF_URL = "https://media.tenor.com/qEna2B80T9gAAAAi/tarot-cards.gif"
# Link ảnh lưng bài chuẩn Rider-Waite
CARD_BACK_URL = "https://w7.pngwing.com/pngs/632/63/png-transparent-tarot-card-back-wands-pips-major-arcana-tarot-blue-tarot-deck-swords-thumbnail.png"

# ==========================================
# 3. THIẾT KẾ GIAO DIỆN (UI/UX)
# ==========================================
st.set_page_config(page_title="Vũ Trụ Thầm Thì", page_icon="🔮", layout="wide")

# Áp dụng Custom CSS cho Dark Theme, Font chữ huyền bí và Clean Layout
st.markdown("""
<style>
    /* Tổng thể Dark Theme */
    .stApp {
        background-color: #0d0118;
        color: #f5e6ff;
        font-family: 'Cinzel', serif; /* Cần Google Font nếu muốn */
    }
    
    /* Font heading */
    h1, h2, h3 {
        color: #e6b3ff !important;
        font-family: 'Cinzel Decorative', cursive;
    }

    /* sidebar style */
    [data-testid="stSidebar"] {
        background-color: #1a0233;
        border-right: 2px solid #3d0566;
    }
    
    /* Button style */
    .stButton>button {
        background-color: #6600cc;
        color: white;
        border: 2px solid #e6b3ff;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #e6b3ff;
        color: #3d0566;
        border-color: #3d0566;
    }
    
    /* Input field style */
    .stTextInput>div>div>input {
        background-color: #2a004d;
        color: #f5e6ff;
        border-color: #3d0566;
    }

    /* Hiển thị lá bài đẹp hơn */
    .card-title {
        text-align: center;
        margin-bottom: 5px;
        color: #e6b3ff;
    }

    /* Chân trang */
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #f5e6ff;
        font-size: 0.9em;
        border-top: 1px solid #3d0566;
        padding-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Thêm Google Fonts vào giao diện
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cinzel+Decorative:wght@400;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# sidebar content
with st.sidebar:
    st.header("🔮 Chào Mừng")
    st.image("https://via.placeholder.com/300x150.png?text=V%C5%A9+Tr%E1%BB%A5+Th%E1%BB%91ng+Nh%E1%BA%A5t", caption="Gặp Gỡ Mystic Vision") # Có thể thay bằng ảnh thật
    st.write("Cánh cửa đến với sự thấu hiểu nội tâm đã mở. Hãy tập trung vào vấn đề của bạn, đặt một câu hỏi chân thành và khi đã sẵn sàng, hãy bấm nút rút bài.")
    st.write("---")
    st.header("💖 Câu Hỏi Hàng Ngày")
    if st.button("Lời khuyên từ vũ trụ hôm nay"):
        # Tính năng câu hỏi nhanh hàng ngày
        st.session_state.today_guidance = True
        user_question = "Hôm nay tôi cần tập trung năng lượng vào điều gì?"
    st.write("---")
    st.header("⚙️ Cài đặt Trải bài")
    tarot_theme = st.selectbox("Chọn Phong cách Hình ảnh:", ["Classic (Rider-Waite)", "Cyberpunk Tarot", "Anime Ghibli Tarot", "Tranh sơn dầu Phục hưng"], index=1)
    
# Main content area
st.title("🌌 Vũ Trụ Thầm Thì: Mystic Vision (Bản Đầy Đủ 78 Lá)")
st.write("Cánh cửa thấu hiểu nội tâm đã mở. Hãy đặt một câu hỏi chân thành.")

# Ô nhập câu hỏi
user_question = st.text_input("Câu hỏi của bạn (VD: Tình hình công việc của tôi tháng tới sẽ ra sao?):")

if st.button("Rút 3 Lá Bài & Bắt đầu Hành Trình"):
    if not user_question:
        st.warning("Bạn phải nhập câu hỏi trước khi bắt đầu hành trình nhé!")
    else:
        # Bắt đầu vòng quay chờ đợi
        with st.spinner('Mystic Vision đang kết nối với năng lượng vũ trụ...'):
            
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
            
            # Hiển thị hiệu ứng trộn bài
            col_shuffle = st.columns([1, 1, 1])
            with col_shuffle[1]:
                st.image(SHUFFLING_GIF_URL, caption="Mystic Vision đang trộn bài...")
                
            # Tạo hiệu ứng chờ nhân tạo (2 giây) để tạo cảm giác
            time.sleep(2)
            
            # --- CÂU LỆNH CHO GEMINI (PROMPT) ---
            system_prompt = f"""
            Bạn là một Master Tarot tên là Mystic Vision. Văn phong bí ẩn, thấu cảm và truyền cảm hứng.
            Người dùng vừa hỏi: '{user_question}'
            Họ bốc được 3 lá bài theo thứ tự Quá Khứ - Hiện Tại - Tương Lai là: 
            1. {drawn_cards[0]}
            2. {drawn_cards[1]}
            3. {drawn_cards[2]}
            
            Hãy giải nghĩa thật sâu sắc, rành mạch từng lá bài, phân tích sự liên kết giữa chúng 
            và đưa ra lời khuyên tổng kết. 
            
            Yêu cầu định dạng lời giải:
            - Sử dụng Markdown để tạo các tiêu đề (Heading) cho từng lá bài (VD: ## Lá bài thứ 1: [Tên Lá Bài] - Quá Khứ).
            - Bôi đậm các từ khóa quan trọng.
            - Phân tích mối liên hệ giữa các lá bài dưới dạng một câu chuyện.
            - Lời khuyên tổng kết rõ ràng dưới dạng một danh sách (VD: 1, 2, 3).
            """
            
            try:
                # --- 1. GỌI GEMINI ĐỂ GIẢI BÀI (VĂN BẢN) ---
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=system_prompt
                )
                interpretation = response.text
                
                # --- 2. GỌI API ĐỂ TẠO HÌNH ẢNH TRỰC QUAN TỔNG THỂ ---
                # Nâng cấp prompt tạo ảnh để chất lượng cao hơn
                image_prompt = f"Digital art, masterpiece, high quality, highly detailed, octane render, unreal engine style, in {tarot_theme} style. A single coherent mystical scene combining the concepts of 3 tarot cards: {drawn_cards[0]}, {drawn_cards[1]}, {drawn_cards[2]}. Moody lighting, spiritual atmosphere, highly artistic."
                
                encoded_prompt = urllib.parse.quote(image_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true"
                
                # --- 3. HIỂN THỊ KẾT QUẢ ---
                # st.success(f"Đã rút thành công: {cards_text}")
                
                # Giao diện chính sau khi rút bài
                st.write("---")
                
                # Phần 1: Tầm Nhìn Trực Quan (Large image)
                st.subheader("I. Tầm Nhìn Trực Quan Về Trải Bài")
                st.image(image_url, caption=f"Bức tranh tổng hợp năng lượng cho trải bài của bạn (Phong cách: {tarot_theme})", use_container_width=True)
                
                # Giao diện chính cho phần Giải bài
                st.write("---")
                st.subheader("II. Thông Điệp Từ Vũ Trụ")
                
                # Chia màn hình làm 2 cột cho phần giải bài
                col1, col2 = st.columns([1, 1.5]) # Cột 2 rộng hơn cho văn bản

                with col1:
                    st.subheader("Tầm Nhìn Trực Quan Về Trải Bài")
                    st.image(image_url, caption=f"Bức tranh tổng hợp năng lượng cho trải bài của bạn (Phong cách: {tarot_theme})", use_container_width=True)
                
                with col2:
                    st.subheader("Thông Điệp Từ Vũ Trụ")
                    st.write(interpretation)

                
                # Phần chân trang
                st.write("---")
                st.markdown("""
                <div class="footer">
                    Mystic Vision &copy; 2023 | Trải nghiệm bói Tarot AI<br>
                    <i>Lưu ý: Bói Tarot chỉ mang tính chất tham khảo, hãy luôn lắng nghe tiếng nói nội tâm và tự chịu trách nhiệm cho các quyết định của mình.</i>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Có lỗi xảy ra khi kết nối vũ trụ: {e}")