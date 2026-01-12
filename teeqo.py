import streamlit as st
from hugchat import hugchat
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# 2. القائمة الجانبية (Sidebar)
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    # عرض صورتك في القائمة الجانبية أيضاً
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=100)
    
    st.write("ارفع ملفاتك ليتعلم منها تيجو (PDF)")
    uploaded_file = st.file_uploader("اسحب الملف هنا", type=['pdf'])

st.title("Tego AI Strategic Advisor")

# 3. إعداد الاتصال بالذكاء الاصطناعي (HuggingChat)
if "chatbot" not in st.session_state:
    try:
        st.session_state.chatbot = hugchat.ChatBot(cookie_path=None)
        id = st.session_state.chatbot.new_conversation()
        st.session_state.chatbot.change_conversation(id)
    except:
        st.session_state.chatbot = None

# 4. إدارة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. عرض الرسائل السابقة مع صورتك الشخصية بدل الروبوت
for message in st.session_state.messages:
    # هنا التعديل: نستخدم صورتك كأفاتار للمساعد (assistant)
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 6. منطقة إدخال المستخدم والرد
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد الرد من المساعد وصورتك تظهر بجانبه
    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if st.session_state.chatbot:
            try:
                with st.spinner("جارِ التفكير..."):
                    response = st.session_state.chatbot.chat(prompt)
                    full_response = str(response)
                    st.markdown(full_response)
            except:
                full_response = "عذراً، أواجه ضغطاً في الطلبات حالياً."
                st.error(full_response)
        else:
            full_response = "أهلاً بك! أنا تيجو، كيف يمكنني مساعدتك اليوم؟"
            st.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})