import streamlit as st
import google.generativeai as genai
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# 2. ضع مفتاحك الجديد هنا (تأكد من نسخه بالكامل من Google AI Studio)
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"

# 3. محاولة الاتصال والتحقق من المفتاح
if API_KEY == "ضع_مفتاحك_هنا" or not API_KEY:
    st.error("⚠️ خطأ: لم تقم بوضع مفتاح API صالح داخل الكود.")
    model = None
else:
    try:
        genai.configure(api_key=API_KEY)
        # استخدام موديل مستقر جداً
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"❌ خطأ في إعدادات المفتاح: {e}")
        model = None

# 4. واجهة المستخدم (Sidebar)
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    st.write("(PDF) ارفع ملفاتك ليتعلم منها تيجو")
    st.file_uploader("اسحب الملف هنا", type=['pdf'])

st.title("Tego AI Strategic Advisor")

# 5. ذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل وصورتك تظهر للردود
for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 6. منطقة الإدخال ومعالجة الرد
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if model:
            try:
                with st.spinner("تيجو يحلل ويجيب..."):
                    response = model.generate_content(prompt)
                    if response:
                        full_response = response.text
                        st.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                # إذا كان المفتاح لا يزال يعطي خطأ
                if "API_KEY_INVALID" in str(e) or "400" in str(e):
                    st.error("❌ المفتاح الذي وضعته غير صالح. يرجى إنشاء مفتاح جديد من Google AI Studio.")
                else:
                    st.error(f"حدث خطأ غير متوقع: {e}")
        else:
            st.info("النظام بانتظار مفتاح API صحيح للعمل.")