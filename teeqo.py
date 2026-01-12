import streamlit as st
from duckduckgo_search import DDGS
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# 2. القائمة الجانبية (Sidebar)
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    # عرض صورتك في القائمة الجانبية
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=100)
    else:
        st.warning("لم يتم العثور على ملف me.png")
    
    st.write("ارفع ملفاتك ليتعلم منها تيجو (PDF)")
    st.file_uploader("اسحب الملف هنا", type=['pdf'])

st.title("Tego AI Strategic Advisor")

# 3. إدارة ذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. عرض الرسائل السابقة مع صورتك الشخصية
for message in st.session_state.messages:
    # نستخدم صورتك كأفاتار للردود
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. وظيفة البحث والرد (مثل جوجل)
def get_ai_response(query):
    try:
        with DDGS() as ddgs:
            # البحث عن ملخص سريع للسؤال
            results = ddgs.text(query, region='wt-wt', safesearch='moderate', timelimit='y')
            if results:
                # نأخذ أول نتيجة ونعرضها كإجابة
                return results[0]['body']
            else:
                return "عذراً، لم أجد معلومات كافية حول هذا الموضوع حالياً."
    except Exception as e:
        return "أواجه مشكلة في الاتصال بالشبكة، يرجى المحاولة مرة أخرى."

# 6. منطقة إدخال المستخدم والرد
if prompt := st.chat_input("اسأل تيجو أي شيء..."):
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد الرد (البحث في الإنترنت) مع صورتك
    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        with st.spinner("جارِ البحث والتحليل..."):
            full_response = get_ai_response(prompt)
            st.markdown(full_response)
            
    # حفظ الرد في السجل
    st.session_state.messages.append({"role": "assistant", "content": full_response})