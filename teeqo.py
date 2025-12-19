import streamlit as st
import google.generativeai as genai
import os
import base64
import re
from PyPDF2 import PdfReader
from gtts import gTTS

# --- 1. الإعدادات والاتصال ---
# المفتاح الخاص بك
API_KEY = "AIzaSyAGlHkK29d3wG19nWlt2ZckcJOjekJQoJM" 

try:
    genai.configure(api_key=API_KEY)
except:
    st.error("⚠️ فشل في إعداد المفتاح، تأكد من صحته.")

MEMORY_FILE = "tego_brain_classic.txt"
IMAGE_PATH = "me.jpg" 

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("أنا تيجو، مساعد ذكي بصوت رجل ناضج.\n")

def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
        except: return None
    return None

MY_AVATAR = get_image_base64(IMAGE_PATH)

# --- 2. محرك الرد الذكي (يتفادى خطأ 404 و Quota) ---
def ask_tego(question):
    try:
        # البحث عن أي موديل متاح في حسابك لتجنب الـ 404
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'gemini-1.5-flash'
        if not any(target in m for m in models):
            target = models[0].split('/')[-1] if models else None
        
        if not target: return "❌ لا يوجد موديل مفعل في حسابك."

        model = genai.GenerativeModel(target)
        context = ""
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                context = f.read()[-1500:]
        
        prompt = f"أنت تيجو، رجل ناضج وواثق. الذاكرة: {context}\nالمستخدم يسأل: {question}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e): return "⚠️ انتهت حصة المفتاح اليوم. جرب مفتاحاً آخر."
        return f"❌ خطأ: {str(e)}"

# --- 3. محرك الصوت الرجالي ---
def speak_male(text):
    if not text or "❌" in text or "⚠️" in text: return
    try:
        clean_text = re.sub(r'[*#_~-]', '', text)
        tts = gTTS(text=clean_text[:300], lang='ar')
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        # كود الصوت يعمل تلقائياً على أغلب المتصفحات
        audio_html = f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except: pass

# --- 4. واجهة المستخدم (تصميم الإصدار الأول مع Sidebar) ---
st.set_page_config(page_title="Tego AI", layout="wide")

# الشريط الجانبي (مركز التعلم القابل للإخفاء)
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🧠 مركز التعلم</h2>", unsafe_allow_html=True)
    st.info("هنا تطور ذاكرة تيجو")
    
    st.divider()
    st.subheader("📁 ملف PDF")
    up_file = st.file_uploader("ارفع ملف:", type=['pdf'])
    if up_file and st.button("حفظ الملف"):
        reader = PdfReader(up_file)
        content = "".join([p.extract_text() for p in reader.pages])
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[بيانات]: {content[:1000]}\n")
        st.success("تم الحفظ!")

    st.divider()
    st.subheader("✍️ معلومة يدوية")
    manual_info = st.text_area("أضف معلومة:", height=100)
    if st.button("حفظ المعلومة"):
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[معلومة]: {manual_info}\n")
        st.success("تم الحفظ!")

    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# الهيدر الرئيسي (صورة تيجو بالأعلى)
st.markdown("<center>", unsafe_allow_html=True)
if MY_AVATAR:
    st.markdown(f'<img src="{MY_AVATAR}" style="width:110px;height:110px;border-radius:50%;border:3px solid #007bff;object-fit:cover;">', unsafe_allow_html=True)
st.title("Tego AI")
st.caption("أنا هنا لمساعدتك ولكي ننظر سوياً")
st.markdown("</center>", unsafe_allow_html=True)

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
col_l, col_main, col_r = st.columns([1, 4, 1])
with col_main:
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