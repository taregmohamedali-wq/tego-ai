import streamlit as st
import google.generativeai as genai
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# 2. إعداد المفتاح (وضعه داخل الكود مباشرة كما طلبت)
# استبدل النجوم بمفتاحك الذي يبدأ بـ AIza
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"حدث خطأ في تهيئة المفتاح: {e}")
    model = None

# 3. القائمة الجانبية (Sidebar)
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=100)
    st.write("(PDF) ارفع ملفاتك ليتعلم منها تيجو")
    st.file_uploader("اسحب الملف هنا", type=['pdf'])

st.title("Tego AI Strategic Advisor")

# 4. إدارة الذاكرة وعرض الرسائل
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    # صورتك تظهر هنا بجانب ردود تيجو
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. استقبال السؤال والرد بذكاء
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    # عرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد الرد من جوجل جيميناي
    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if model:
            try:
                with st.spinner("تيجو يفكر الآن..."):
                    response = model.generate_content(prompt)
                    full_response = response.text
                    st.markdown(full_response)
            except Exception as e:
                full_response = "عذراً، المفتاح قد يكون غير صحيح أو هناك مشكلة في الاتصال."
                st.error(f"خطأ: {e}")
        else:
            full_response = "النظام غير جاهز للرد حالياً."
            st.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})