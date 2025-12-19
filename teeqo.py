import streamlit as st
import requests
import os
import base64
from PyPDF2 import PdfReader

# محاولة استيراد مكتبة الصوت
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# --- 1. الإعدادات الأساسية ---
API_KEY = "AIzaSyA29ifogr_JsHRKpXIy9IimSR9MWTwYgg0" 
MEMORY_FILE = "tego_brain.txt"
IMAGE_PATH = "me.jpg"  # تأكد أن ملف الصورة موجود بهذا الاسم في نفس المجلد

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("سجل ذاكرة تيجو:\n")

# وظيفة لتحويل الصورة إلى كود لعرضها
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    return None

MY_AVATAR = get_image_base64(IMAGE_PATH)

# --- 2. محرك الرد المحدث (لتجنب خطأ v1beta) ---
def ask_tego(question):
    # استخدام رابط v1 بدلاً من v1beta لحل المشكلة التي ظهرت في صورتك
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        context = f.read()[-2000:]

    payload = {
        "contents": [{"parts": [{"text": f"الذاكرة: {context}\nالمستخدم: {question}\nرد كـ Tego:"}]}]
    }
    try:
        response = requests.post(url, json=payload, timeout=20)
        res_data = response.json()
        if response.status_code == 200:
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            # محاولة أخيرة برابط v1beta في حال فشل v1
            url_beta = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            response = requests.post(url_beta, json=payload, timeout=20)
            return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "⚠️ عذراً، هناك مشكلة في الاتصال بسيرفرات جوجل حالياً."

# --- 3. تصميم واجهة المستخدم ---
st.set_page_config(page_title="Tego AI Pro", layout="wide")

# عرض الصورة الشخصية في الأعلى
col1, col2 = st.columns([1, 6])
with col1:
    if MY_AVATAR:
        st.markdown(f'<img src="{MY_AVATAR}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #007bff;">', unsafe_allow_html=True)
with col2:
    st.title("Tego AI: ")

st.markdown("---")

# القائمة الجانبية (مركز التعلم)
with st.sidebar:
    st.header("🧠 مركز التعلم")
    uploaded_file = st.file_uploader("ارفع ملف PDF ليتعلمه تيجو:", type=['pdf'])
    if uploaded_file and st.button("تغذية من الملف"):
        reader = PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in reader.pages])
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[محتوى ملف {uploaded_file.name}]: {text}\n")
        st.success("تم التعلم من الملف!")

    st.divider()
    manual_info = st.text_area("أو أضف معلومة يدوية:")
    if st.button("حفظ المعلومة"):
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[معلومة]: {manual_info}\n")
        st.success("تم الحفظ!")

# --- 4. الدردشة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = MY_AVATAR if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("تحدث مع تيجو..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant", avatar=MY_AVATAR):
        answer = ask_tego(prompt)
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})