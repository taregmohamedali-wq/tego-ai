import streamlit as st
from g4f.client import Client

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# 2. تنسيق الواجهة (تصحيح الخطأ هنا)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div.stButton > button:first-child {
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True) # تم تصحيح هذا السطر

# 3. القائمة الجانبية (Sidebar)
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    st.write("ارفع ملفاتك ليتعلم منها تيجو (PDF)")
    uploaded_file = st.file_uploader("اسحب الملف هنا", type=['pdf'])

st.title("Tego AI Strategic Advisor")

# 4. إعداد الاتصال بالذكاء الاصطناعي (بدون مفتاح)
client = Client()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. منطقة الدردشة
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # محاولة جلب رد مجاني من الإنترنت
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
        except Exception as e:
            full_response = "عذراً، الخادم المجاني مشغول حالياً. حاول مرة أخرى."
            st.error(f"حدث خطأ: {e}")
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})