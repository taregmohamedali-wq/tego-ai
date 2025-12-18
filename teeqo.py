import streamlit as st
import requests
import os
import base64
import time
from PyPDF2 import PdfReader

# --- 1. الإعدادات ---
# ملاحظة: يفضل مستقبلاً وضع المفتاح في Streamlit Secrets للأمان
API_KEY = "AIzaSyAaixKmeK3og1N2MfZkoLt15JQyFSwdNKY"
MEMORY_FILE = "tego_final_memory.txt"
IMAGE_PATH = "me.jpg" 

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("أنا Tego، مساعدك الشخصي الذكي.\n")

def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
        except: return None
    return None

MY_AVATAR = get_image_base64(IMAGE_PATH)

# --- 2. محرك الاتصال الذكي (حل مشكلة الموديلات والكوتا) ---

def ask_tego(question):
    # قائمة الموديلات التي تدعمها جوجل حالياً بالترتيب
    model_options = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-1.0-pro"
    ]
    
    # جلب سياق الذاكرة
    context = ""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            context = f.read()[-3000:]

    payload = {
        "contents": [{"parts": [{"text": f"الذاكرة التاريخية: {context}\nالمستخدم: {question}\nأجب كشخصية Tego:"}]}]
    }

    # محاولة الاتصال عبر مسارات مختلفة (v1 و v1beta)
    for ver in ["v1beta", "v1"]:
        for model in model_options:
            url = f"https://generativelanguage.googleapis.com/{ver}/{model}:generateContent?key={API_KEY}"
            try:
                response = requests.post(url, json=payload, timeout=20)
                res_data = response.json()
                
                if response.status_code == 200:
                    return res_data['candidates'][0]['content']['parts'][0]['text']
                
                # إذا كانت المشكلة هي "تجاوز الحصة" (Quota)
                elif "quota" in str(res_data).lower():
                    time.sleep(10) # انتظر قليلاً ثم حاول الموديل التالي
                    continue
            except:
                continue
                
    return "⚠️ جميع المحاولات فشلت حالياً بسبب ضغط سيرفرات جوجل أو قيود الحصة المجانية. يرجى المحاولة بعد دقيقة."

# --- 3. تصميم واجهة الموبايل ---

st.set_page_config(page_title="Tego AI", layout="centered")

# الهيدر
h_col1, h_col2 = st.columns([1, 4])
with h_col1:
    if MY_AVATAR:
        st.markdown(f'<img src="{MY_AVATAR}" style="width:70px; height:70px; border-radius:50%; object-fit:cover; border:2px solid #007bff;">', unsafe_allow_html=True)
with h_col2:
    st.title("Tego AI")
    st.caption("نظام المحادثة والذاكرة السحابي")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=MY_AVATAR if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

# إدخال المستخدم
if prompt := st.chat_input("تحدث مع Tego..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=MY_AVATAR):
        with st.spinner("جاري استحضار الرد..."):
            answer = ask_tego(prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# القائمة الجانبية
with st.sidebar:
    st.header("⚙️ الإعدادات")
    uploaded_file = st.file_uploader("تغذية الذاكرة (PDF/TXT):", type=['txt', 'pdf'])
    if uploaded_file and st.button("حفظ المعلومات"):
        text = ""
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages: text += page.extract_text()
        else:
            text = uploaded_file.getvalue().decode("utf-8")
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{text}\n")
        st.success("تم التحديث!")
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()