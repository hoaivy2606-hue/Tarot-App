import streamlit as st
from google import genai
import random
import urllib.parse
import time
from PIL import Image
import requests
from io import BytesIO

# ==========================================
# 1. CẤU HÌNH API KEY (DÙNG STREAMLIT SECRETS)
# ==========================================
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "DUNG_DANG_API_KEY_THAT_VAO_DAY_DE_CHAY_LOCAL"

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

SHUFFLING_GIF_URL = "https://media.tenor.com/qEna2B80T9gAAAAi/tarot-cards.gif"
CARD_BACK_URL = "https://w7.pngwing.com/pngs/632/63/png-transparent-tarot-card-back-wands-pips-major-arcana-tarot-blue-tarot-deck-swords-thumbnail.png"

# ==========================================
# 3. THIẾT KẾ GIAO DIỆN (UI/UX)
# ==========================================
st.set_page_config(page_title="Vũ Trụ Thầm Thì", page_icon="🔮", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d0118; color: #f5e6ff; font-family: 'Cinzel', serif; }
    h1, h2, h3 { color: #e6b3ff !important; font-family: 'Cinzel Decorative', cursive; }
    [data-testid="stSidebar"] { background-color: #1a0233; border-right: 2px solid #3d0566; }
    .sidebar-logo { text-align: center; margin-top: -30px; margin-bottom: 20px; }
    .stButton>button { background-color: #6600cc; color: white; border: 2px solid #e6b3ff; border-radius: 10px; font-weight: bold; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #e6b3ff; color: #3d0566; border-color: #3d0566; }
    .stTextInput>div>div>input { background-color: #2a004d; color: #f5e6ff; border-color: #3d0566; }
    .signature { font-family: 'Cinzel', serif; font-size: 1.1rem; color: #e6b3ff; text-align: left; margin-top: -15px; margin-bottom: 30px; font-weight: bold; }
    .stImage > div > img { border-radius: 10px; border: 1px solid #3d0566; }
    .footer { text-align: center; margin-top: 50px; color: #f5e6ff; font-size: 0.9em; border-top: 1px solid #3d0566; padding-top: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cinzel+Decorative:wght@400;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)

with st.sidebar:
    st.header("🔮 Chào Mừng")
    st.markdown('<div class="sidebar-logo"><span style="font-size: 5rem;">🔮</span></div>', unsafe_allow_html=True)
    st.write("Cánh cửa đến với sự thấu hiểu nội tâm đã mở. Hãy tập trung vào vấn đề của bạn, đặt một câu hỏi chân thành và khi đã sẵn sàng, hãy bấm nút rút bài.")
    st.write("---")
    st.header("⚙️ Cài đặt Trải bài")
    tarot_theme = st.selectbox("Chọn Phong cách Hình ảnh:", ["Classic (Rider-Waite)", "Cyberpunk Tarot", "Anime Ghibli Tarot", "Tranh sơn dầu Phục hưng"], index=1)
    st.write("---")
    st.header("💖 Câu Hỏi Hàng Ngày")
    if st.button("Lời khuyên từ vũ trụ hôm nay"):
        st.session_state.today_guidance = True
        user_question = "Hôm nay tôi cần tập trung năng lượng vào điều gì?"

st.title("🌌 Vũ Trụ Thầm Thì: Mystic Vision")
st.markdown('<div class="signature">performing by @nkhang036</div>', unsafe_allow_html=True)
st.write("Cánh cửa thấu hiểu nội tâm đã mở. Hãy đặt một câu hỏi chân thành.")

user_question = st.text_input("Câu hỏi của bạn (VD: Tình hình công việc của tôi tháng tới sẽ ra sao?):")

if st.button("Rút 3 Lá Bài & Bắt đầu Hành Trình"):
    if not user_question:
        st.warning("Bạn phải nhập câu hỏi trước khi bắt đầu hành trình nhé!")
    else:
        # Khai báo biến TRƯỚC khối try để tránh lỗi NameError vĩnh viễn
        is_using_fallback = False
        image_to_display = CARD_BACK_URL
        interpretation = ""
        
        with st.spinner('Mystic Vision đang kết nối với năng lượng vũ trụ...'):
            try:
                # --- RÚT BÀI VÀ XÁC ĐỊNH CHIỀU XUÔI/NGƯỢC ---
                drawn_cards_raw = random.sample(TAROT_DECK, 3)
                drawn_cards = []
                for card in drawn_cards_raw:
                    is_reversed = random.choice([True, False])
                    drawn_cards.append(f"{card} (Ngược)" if is_reversed else f"{card} (Xuôi)")
                        
                # Hiển thị hiệu ứng trộn bài
                col_shuffle = st.columns([1, 1, 1])
                with col_shuffle[1]:
                    st.image(SHUFFLING_GIF_URL, caption="Mystic Vision đang trộn bài...")
                time.sleep(2)
                
                # --- GỌI GEMINI ĐỂ GIẢI BÀI ---
                system_prompt = f"""
                Bạn là một Master Tarot kì cựu tên là Mystic Vision. Văn phong trung thực, kĩ càng, nói thẳng vấn đề, không bao che.
                Người dùng vừa hỏi: '{user_question}'
                Họ bốc được 3 lá bài theo thứ tự Quá Khứ - Hiện Tại - Tương Lai là: 
                1. {drawn_cards[0]}
                2. {drawn_cards[1]}
                3. {drawn_cards[2]}
                
                Hãy giải nghĩa thật kĩ càng từng lá bài, phân tích sâu sắc mối liên hệ giữa chúng dưới góc độ nhân quả, sự thật trần trụi và không bao che. Đừng dùng những lời lẽ truyền cảm hứng sáo rỗng. Hãy nói thẳng vấn đề mà người dùng cần phải đối mặt.
                Yêu cầu định dạng lời giải: Sử dụng Markdown tạo tiêu đề rõ ràng, bôi đậm từ khóa quan trọng, phân tích logic, đưa lời khuyên thực tế và thẳng thắn.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=system_prompt
                )
                interpretation = response.text
                
                # --- TẠO ẢNH BẰNG POLLINATIONS ---
                image_prompt = f"Digital fantasy art, masterpiece, high quality, highly detailed, in {tarot_theme} style. A single coherent mystical scene synthesizing the core concepts, symbols, and atmosphere of the 3 tarot cards: {drawn_cards_raw[0]}, {drawn_cards_raw[1]}, {drawn_cards_raw[2]}. The overall vibe should be dark and confronting yet truthful. Moody lighting, highly artistic."
                encoded_prompt = urllib.parse.quote(image_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true"
                
                # --- CƠ CHẾ FALLBACK ---
                try:
                    img_requests = requests.get(image_url, timeout=15) 
                    if img_requests.status_code == 200 and img_requests.content:
                        image_to_display = Image.open(BytesIO(img_requests.content))
                    else:
                        is_using_fallback = True
                except:
                    is_using_fallback = True
                    
            except Exception as e:
                st.error(f"Có lỗi xảy ra trong quá trình giải bài: {e}")
                
        # --- HIỂN THỊ KẾT QUẢ (Nằm ngoài khối try để đảm bảo luôn chạy an toàn) ---
        if interpretation: # Chỉ hiển thị khi có lời giải thành công
            st.write("---")
            col1, col2 = st.columns([1.2, 1])

            with col1:
                st.subheader("I. Tầm Nhìn Trực Quan Về Trải Bài")
                st.image(image_to_display, caption=f"Bức tranh tổng hợp năng lượng cho trải bài của bạn (Phong cách: {tarot_theme})", use_container_width=True)
                if is_using_fallback:
                    st.warning("⚠️ Bức tranh nghệ thuật tạm thời không load được do AI tạo ảnh quá tải. Hệ thống đang sử dụng ảnh mặt lưng bài thay thế. Bạn có thể rút lại để xem tranh!")
            
            with col2:
                st.subheader("II. Thông Điệp Từ Vũ Trụ")
                st.write(interpretation)

st.write("---")
st.markdown("""
<div class="footer">
    Mystic Vision &copy; 2023 | Trải nghiệm bói Tarot AI kĩ càng | Chữ ký: performed by @nkhang036<br>
    <i>Lưu ý: Bói Tarot chỉ mang tính chất tham khảo, hãy luôn lắng nghe tiếng nói nội tâm và tự chịu trách nhiệm cho các quyết định của mình.</i>
</div>
""", unsafe_allow_html=True)