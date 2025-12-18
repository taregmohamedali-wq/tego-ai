import streamlit as st
import requests
import os
import base64
import time
from PyPDF2 import PdfReader

# --- 1. الإعدادات الأساسية ---
API_KEY = "AIzaSyAaixKmeK3og1N2MfZkoLt15JQyFSwdNKY"
MEMORY_FILE = "tego_memory.txt"
IMAGE_PATH = "me.jpg" 

# إعداد ملف الذاكرة
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("أنا Tego، مساعدك الذكي.\n")

# معالجة الصورة الشخصية لتظهر في الدردشة
def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
        except: return None
    return None

MY_AVATAR = get_image_base64(IMAGE_PATH)

# --- 2. محرك الاتصال الذكي (إصلاح أخطاء المسار والزحام) ---

def ask_tego(question):
    # استخدام المسار الأكثر استقراراً وشمولية
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # جلب السياق من الذاكرة
    context = ""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            context = f.read()[-3000:] # جلب آخر 3000 حرف فقط لسرعة الرد

    payload = {
        "contents": [{"parts": [{"text": f"الذاكرة التاريخية:\n{context}\n\nسؤال المستخدم: {question}\nرد كـ Tego باختصار وبذكاء:"}]}]
    }

    try:
        # نظام المحاولات في حال وجود ضغط (Quota)
        for attempt in range(2):
            response = requests.post(url, json=payload, timeout=25)
            res_data = response.json()
            
            if response.status_code == 200:
                return res_data['candidates'][0]['content']['parts'][0]['text']
            
            # إذا كان الخطأ بسبب كثرة الطلبات (429)
            elif response.status_code == 429 or "quota" in str(res_data).lower():
                time.sleep(10) # انتظر 10 ثوانٍ وحاول مرة أخرى
                continue
            else:
                return f"❌ خطأ من جوجل: {res_data.get('error', {}).get('message', 'حدث خطأ غير معروف')}"
    except Exception as e:
        return f"⚠️ عطل في الاتصال: {str(e)}"
        
    return "⚠️ جوجل يطلب الانتظار دقيقة بسبب ضغط الاستخدام المجاني."

# --- 3. واجهة المستخدم (تصميم مثالي للموبايل) ---

st.set_page_config(page_title="Tego AI Pro", layout="centered")

# تنسيق الرأس (صورتك الشخصية واسم التطبيق)
header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    if MY_AVATAR:
        st.markdown(f'<img src="{MY_AVATAR}" style="width:70px; height:70px; border-radius:50%; object-fit:cover; border:2px solid #007bff;">', unsafe_allow_html=True)
with header_col2:
    st.title("Tego AI")
    st.caption("نسخة الموبايل المستقرة - 2025")

st.divider()

# سجل المحادثة في الجلسة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    avatar_img = MY_AVATAR if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar_img):
        st.markdown(msg["content"])

# منطقة إدخال النص
if prompt := st.chat_input("تحدث مع Tego..."):
    # إضافة سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # طلب الرد من Tego
    with st.chat_message("assistant", avatar=MY_AVATAR):
        with st.spinner("Tego يفكر..."):
            answer = ask_tego(prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 4. مركز التحكم الجانبي (أرشفة الملفات) ---
with st.sidebar:
    st.header("📂 ذاكرة Tego")
    uploaded_file = st.file_uploader("ارفع ملف PDF أو TXT للتعلم منه:", type=['txt', 'pdf'])
    
    if uploaded_file and st.button("حفظ المعلومات"):
        text = ""
        try:
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                for page in reader.pages: text += page.extract_text()
            else:
                text = uploaded_file.getvalue().decode("utf-8")
            
            # كتابة المحتوى في ملف الذاكرة
            with open(MEMORY_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n[بيانات من ملف {uploaded_file.name}]:\n{text}\n")
            st.success("تم تحديث ذاكرة Tego بنجاح!")
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {e}")

    st.divider()
    if st.button("🗑️ مسح المحادثة الحالية"):
        st.session_state.messages = []
        st.rerun()