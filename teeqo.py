import streamlit as st
import google.generativeai as genai
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# 2. إعداد المفتاح (تأكد من وضعه بشكل صحيح هنا)
API_KEY = "AIzaSy..." # ضع مفتاحك هنا

try:
    genai.configure(api_key=API_KEY)
    # استخدام gemini-pro لضمان أعلى توافق واستقرار
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"حدث خطأ في التهيئة: {e}")
    model = None

# 3. القائمة الجانبية
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=100)
    st.write("(PDF) ارفع ملفاتك ليتعلم منها تيجو")
    st.file_uploader("اسحب الملف هنا", type=['pdf'])

st.title("Tego AI Strategic Advisor")

# 4. الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. الاستجابة
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if model:
            try:
                with st.spinner("تيجو يفكر الآن..."):
                    # إرسال السؤال
                    response = model.generate_content(prompt)
                    # معالجة النص المستلم بأمان
                    full_response = response.text
                    st.markdown(full_response)
            except Exception as e:
                full_response = "عذراً، أحتاج لتحديث الموديل. جرب إرسال الرسالة مرة أخرى."
                st.error(f"خطأ في الموديل: {e}")
        else:
            full_response = "النظام غير جاهز."
            st.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})