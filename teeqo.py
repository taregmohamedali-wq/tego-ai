import streamlit as st
import google.generativeai as genai
import os
import base64
import re
from PyPDF2 import PdfReader
from gtts import gTTS

# --- 1. الإعدادات والاتصال ---
API_KEY = "AIzaSyAGlHkK29d3wG19nWlt2ZckcJOjekJQoJM" 
genai.configure(api_key=API_KEY)

MEMORY_FILE = "tego_brain_classic.txt"
IMAGE_PATH = "me.jpg" 

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("أنا تيجو، مساعد ذكي بصوت رجل ناضج.\n")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    return None

MY_AVATAR = get_image_base64(IMAGE_PATH)

# --- 2. محرك الرد الذكي (الحل النهائي لخطأ 404) ---
def ask_tego(question):
    try:
        # البحث عن أي موديل متاح يدعم توليد المحتوى في حسابك
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not models:
            return "❌ لا يوجد موديل متاح في حسابك. تأكد من تفعيل Gemini API."
        
        # ترتيب الأولويات: يبحث عن flash أولاً، ثم pro، ثم أي موديل متاح
        target_model = None
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro']:
            if preferred in models:
                target_model = preferred
                break
        
        if not target_model:
            target_model = models[0] # اختر أول موديل متاح إذا لم يجد المفضلين

        # استدعاء الموديل المختار ديناميكياً
        model = genai.GenerativeModel(target_model)
        
        context = ""
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                context = f.read()[-2000:]
        
        prompt = f"أنت تيجو، رجل ناضج وواثق. الذاكرة: {context}\nالمستخدم: {question}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e): return "⚠️ انتهت حصة المفتاح اليوم."
        return f"❌ خطأ: {str(e)}"

# --- 3. محرك الصوت الرجالي ---
def speak_male(text):
    if not text or "❌" in text or "⚠️" in text: return
    clean_text = re.sub(r'[*#_~-]', '', text)
    tts = gTTS(text=clean_text[:300], lang='ar')
    tts.save("voice.mp3")
    with open("voice.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    audio_html = f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

# --- 4. واجهة المستخدم (التصميم الكلاسيكي + Sidebar) ---
st.set_page_config(page_title="Tego AI", layout="wide")

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🧠 مركز التعلم</h2>", unsafe_allow_html=True)
    st.info("تغذية ذاكرة تيجو بالملفات أو المعلومات اليدوية.")
    st.divider()
    
    st.subheader("📁 رفع ملف PDF")
    up_file = st.file_uploader("اختر ملف:", type=['pdf'])
    if up_file and st.button("حفظ الملف"):
        reader = PdfReader(up_file)
        content = "".join([p.extract_text() for p in reader.pages])
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[بيانات ملف]: {content[:1000]}\n")
        st.success("تم الحفظ!")
    
    st.divider()
    st.subheader("✍️ إضافة معلومة")
    manual_info = st.text_area("اكتب معلومة:", height=150)
    if st.button("حفظ المعلومة"):
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[معلومة]: {manual_info}\n")
        st.success("تم الحفظ!")
    
    st.divider()
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# الهيدر الرئيسي
st.markdown("<center>", unsafe_allow_html=True)
if MY_AVATAR:
    st.markdown(f'<img src="{MY_AVATAR}" style="width:110px;height:110px;border-radius:50%;border:3px solid #007bff;object-fit:cover;">', unsafe_allow_html=True)
st.title("Tego AI")
st.caption("أنا هنا لمساعدتك ولكي ننظر سوياً")
st.markdown("</center>", unsafe_allow_html=True)

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

col_l, col_main, col_r = st.columns([1, 3, 1])

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