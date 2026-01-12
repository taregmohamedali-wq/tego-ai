import streamlit as st
import google.generativeai as genai
import os

# إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية (تأكد أن اسمها me.png بجانب الملف)
USER_IMAGE = "me.png"

# --- [ضع مفتاحك الجديد هنا بدقة] ---
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA" 
# ----------------------------------

# تهيئة الاتصال
try:
    if API_KEY and API_KEY != "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA":
        genai.configure(api_key=API_KEY)
        # استخدام flash لضمان السرعة والتوافق
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.warning("الرجاء التأكد من كتابة مفتاح API صحيح داخل الكود.")
        model = None
except Exception as e:
    st.error(f"خطأ في التهيئة: {e}")
    model = None

# الواجهة الجانبية
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=100)
    st.write("(PDF) ارفع ملفاتك ليتعلم منها تيجو")
    st.file_uploader("اسحب الملف هنا", type=['pdf'])

st.title("Tego AI Strategic Advisor")

# إدارة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# منطقة الإدخال والرد
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if model:
            try:
                with st.spinner("تيجو يفكر..."):
                    response = model.generate_content(prompt)
                    # التحقق من وجود رد نصي
                    if response.text:
                        full_response = response.text
                        st.markdown(full_response)
                    else:
                        full_response = "اعتذر، لم أستطع تكوين رد حالياً."
                        st.write(full_response)
            except Exception as e:
                # عرض رسالة واضحة للمستخدم في حال كان المفتاح غير صالح
                if "API key not valid" in str(e):
                    st.error("المفتاح المستخدم غير صالح. يرجى التأكد من نسخه بالكامل من Google AI Studio.")
                else:
                    st.error(f"حدث خطأ أثناء الاتصال: {e}")
                full_response = "خطأ في الاتصال."
        else:
            full_response = "النظام غير متصل بالخادم."
            st.info(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})