import streamlit as st
from g4f.client import Client

# 1. إعدادات الصفحة والجماليات
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# تنسيق CSS لجعل الواجهة تشبه صورتك الأصلية (الوضع الداكن)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_config=True)

# 2. العنوان الجانبي (Sidebar) كما في صورتك
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    st.write(":ارفع ملفاتك ليتعلم منها تيجو (PDF)")
    uploaded_file = st.file_uploader("Drag and drop file here", type=['pdf'], help="Limit 200MB per file")
    if st.button("Browse files"):
        pass # هنا يمكن إضافة كود معالجة الملفات لاحقاً

st.title("Tego AI Strategic Advisor")

# 3. إعداد محرك الذكاء الاصطناعي (بدون مفتاح API)
client = Client()

# 4. إدارة ذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة بتنسيق جميل
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. منطقة إدخال المستخدم والرد
if prompt := st.chat_input("...تحدث مع تيجو بذكاء"):
    # إضافة عرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد الرد من الإنترنت
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # الاتصال بالمزودين المجانيين عبر الإنترنت تلقائياً
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[{"role": "user", "content": prompt}],
            )
            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = "أواجه مشكلة حالياً في الوصول للمزودين المجانيين. يرجى المحاولة بعد لحظات."
            st.error("فشل الاتصال بالخادم المجاني.")
            
    # حفظ رد الذكاء الاصطناعي في الذاكرة
    st.session_state.messages.append({"role": "assistant", "content": full_response})