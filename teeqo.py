import streamlit as st
import google.generativeai as genai
import os
import base64
import re
from PyPDF2 import PdfReader
from gtts import gTTS

# --- 1. الإعدادات ---
API_KEY = "AIzaSyC8cemzqzJIojHsWAmmlSzizSLG0sJqp-M" 

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"خطأ في إعداد المفتاح: {e}")

MEMORY_FILE = "tego_brain_master.txt"
IMAGE_PATH = "me.jpg" 

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    return None

MY_AVATAR = get_image_base64(IMAGE_PATH)

# --- 2. محرك الرد الذكي (صوت رجل) ---
def ask_tego(question):
    try:
        # فحص الموديلات المتاحة لتفادي خطأ 404
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'gemini-1.5-flash'
        if not any(target in m for m in models):
            target = models[0].split('/')[-1] if models else 'gemini-pro'

        model = genai.GenerativeModel(target)
        
        context = ""
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                context = f.read()[-1500:]

        prompt = f"أنت تيجو، مساعد ذكي بشخصية رجل ناضج. الذاكرة السابقة: {context}\nالسؤال: {question}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e): return "⚠️ الحصة المجانية انتهت لهذا اليوم."
        return f"❌ خطأ تقني: {str(e)}"

# --- 3. محرك النطق الرجالي ---
def speak_male(text):
    if not text or "❌" in text: return
    clean_text = re.sub(r'[*#_~-]', '', text)
    tts = gTTS(text=clean_text[:300], lang='ar')
    tts.save("voice.mp3")
    with open("voice.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    audio_html = f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

# --- 4. تصميم الواجهة (الإصدار الأول + جانبية) ---
st.set_page_config(page_title="Tego AI", layout="wide")

# المركز الجانبي (إخفاء وإظهار)
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🧠 مركز التعلم</h2>", unsafe_allow_html=True)
    st.divider()
    
    st.subheader("📁 ملف PDF")
    up_file = st.file_uploader("ارفع ملف:", type=['pdf'])
    if up_file and st.button("تغذية من ملف"):
        reader = PdfReader(up_file)
        content = "".join([p.extract_text() for p in reader.pages])
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[Data]: {content[:1000]}\n")
        st.success("تم الحفظ!")

    st.divider()
    st.subheader("✍️ كتابة معلومة")
    manual_info = st.text_area("أدخل معلومة يدوية:", height=100)
    if st.button("حفظ المعلومة"):
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[Info]: {manual_info}\n")
        st.success("تم الحفظ!")

# الهيدر الكلاسيكي
st.markdown("<center>", unsafe_allow_html=True)
if MY_AVATAR:
    st.markdown(f'<img src="{MY_AVATAR}" style="width:110px;height:110px;border-radius:50%;border:3px solid #007bff;object-fit:cover;">', unsafe_allow_html=True)
st.title("Tego AI")
st.caption("أنا هنا لمساعدتك ولكي ننظر سوياً")
st.markdown("</center>", unsafe_allow_html=True)

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# الدردشة في المنتصف
c1, c2, c3 = st.columns([1, 4, 1])
with c2:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=MY_AVATAR if msg["role"]=="assistant" else None):
            st.markdown(msg["content"])

    if prompt := st.chat_input("تحدث مع تيجو..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar=MY_AVATAR):
            answer = ask_tego(prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            speak_male(answer)