import streamlit as st
import google.generativeai as genai
import os

# إعدادات الصفحة
st.set_page_config(page_title="Tego AI ", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# جلب المفتاح بأمان من Secrets
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"])
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("الرجاء إضافة المفتاح في إعدادات Secrets.")
        model = None
except:
    st.error("حدث خطأ في الاتصال بخادم الذكاء الاصطناعي.")
    model = None

# القائمة الجانبية (Sidebar)
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=100)
    st.write("ارفع ملفاتك ليتعلم منها تيجو (PDF)")
    st.file_uploader("اسحب الملف هنا", type=['pdf'])

st.title("Tego AI Strategic Advisor")

# إدارة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة مع صورتك الشخصية كأفاتار للمساعد
for message in st.session_state.messages:
    # المساعد يظهر بصورتك، المستخدم يظهر بالأيقونة الافتراضية
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# منطقة الدردشة
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    # رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # رد تيجو (باستخدام الذكاء الاصطناعي الحقيقي)
    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if model:
            try:
                with st.spinner("تيجو يفكر الآن..."):
                    # إرسال السؤال لجوجل جيميناي
                    response = model.generate_content(prompt)
                    full_response = response.text
                    st.markdown(full_response)
            except Exception as e:
                full_response = "عذراً، الخادم مشغول حالياً. يرجى المحاولة بعد قليل."
                st.error(f"خطأ: {e}")
        else:
            full_response = "أهلاً بك! أنا تيجو، يرجى إعداد الاتصال بالخادم أولاً."
            st.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})