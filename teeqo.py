import streamlit as st
import requests
import os
import base64
import pyttsx3
import re
from PyPDF2 import PdfReader

# --- 1. الإعدادات ---
# ملاحظة: إذا استمر الخطأ، يرجى استخراج مفتاح جديد تماماً
API_KEY = "AIzaSyA29ifogr_JsHRKpXIy9IimSR9MWTwYgg0" 
MEMORY_FILE = "brain_tego.txt"
IMAGE_PATH = "me.jpg" 

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("ذاكرة تيجو:\n")

def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
        except: return None
    return None

MY_AVATAR = get_image_base64(IMAGE_PATH)

# --- 2. محرك الصوت (صوت رجل - ثنائي اللغة) ---
def speak_tego(text):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        # تنظيف النص من الرموز لضمان نطق سليم
        clean_text = text.replace("*", "").replace("#", "").replace("-", "")
        
        # اكتشاف اللغة (عربي أم إنجليزي)
        is_arabic = bool(re.search(r'[\u0600-\u06FF]', text))
        
        # البحث عن صوت رجل مناسب في جهازك
        found_voice = False
        for voice in voices:
            if is_arabic and ("Arabic" in voice.name or "ar" in voice.languages):
                engine.setProperty('voice', voice.id)
                found_voice = True
                break
            elif not is_arabic and ("English" in voice.name or "en" in voice.languages):
                # البحث عن صوت رجل إنجليزي (David أو Male)
                if "male" in voice.name.lower() or "david" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    found_voice = True
                    break
        
        if not found_voice:
            engine.setProperty('voice', voices[0].id)

        engine.setProperty('rate', 160)
        engine.say(clean_text)
        engine.runAndWait()
        engine.stop()
    except:
        pass

# --- 3. محرك الرد (حل خطأ 404 وتعديل الإصدار) ---
def ask_tego(question):
    # تم تغيير v1beta إلى v1 لحل مشكلة "Not Found"
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    context = ""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            context = f.read()[-2000:]

    payload = {
        "contents": [{
            "parts": [{
                "text": f"الذاكرة السابقة: {context}\nأجب كـ تيجو بصوت واثق: {question}"
            }]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        res_json = response.json()
        
        if response.status_code == 200:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # محاولة أخيرة عبر v1beta في حال كان حسابك لا يدعم v1 بعد
            url_beta = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            retry = requests.post(url_beta, json=payload, timeout=20)
            return retry.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ خطأ في الاتصال: يرجى التأكد من الـ API Key وقوة الإنترنت."

# --- 4. الواجهة الرسومية ---
st.set_page_config(page_title="Tego AI", layout="wide")

# الهيدر مع صورتك الشخصية
h_col1, h_col2 = st.columns([1, 6])
with h_col1:
    if MY_AVATAR:
        st.markdown(f'<img src="{MY_AVATAR}" style="width:90px;height:90px;border-radius:50%;border:3px solid #007bff;object-fit:cover;">', unsafe_allow_html=True)
with h_col2:
    st.title("Tego AI")
    st.caption("أنا تيجو، أتحدث معك وأتعلم من معلوماتك.")

st.divider()

# القائمة الجانبية للتعلم
with st.sidebar:
    st.header("🧠 مركز التعلم")
    uploaded_file = st.file_uploader("رفع ملف (PDF) ليتعلمه تيجو:", type=['pdf'])
    if uploaded_file and st.button("تغذية الذاكرة"):
        reader = PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in reader.pages])
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[بيانات ملف]: {text}\n")
        st.success("تم التعلم من الملف!")
    
    st.divider()
    manual_info = st.text_area("أضف معلومة يدوية:")
    if st.button("حفظ"):
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[معلومة]: {manual_info}\n")
        st.success("تم الحفظ!")

# نظام الدردشة
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=MY_AVATAR if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("تحدث مع تيجو..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant", avatar=MY_AVATAR):
        with st.spinner("تيجو يحلل الرد..."):
            answer = ask_tego(prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            # نطق الإجابة
            speak_tego(answer)