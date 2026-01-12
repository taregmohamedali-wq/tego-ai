import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# 2. إعداد المفتاح والموديل
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA" # تأكد من وضع مفتاحك الصحيح

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("الرجاء إضافة مفتاح API.")

# 3. القائمة الجانبية (خيار اللغة ورفع الملفات)
with st.sidebar:
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    
    st.title("مركز تحكم تيجو 🧠")
    
    # خيار اختيار اللغة
    language = st.radio("اختر لغة الحوار / Choose Language:", ("العربية", "English"))
    
    st.write("---")
    st.write("📂 تحليل الملفات الاستراتيجية")
    uploaded_file = st.file_uploader("ارفع ملف PDF ليتعلمه تيجو", type=['pdf'])

# وظيفة استخراج النص من الـ PDF
def get_pdf_text(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# 4. إدارة ذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. معالجة السؤال والذكاء الاصطناعي
if prompt := st.chat_input("تحدث مع تيجو..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        with st.spinner("تيجو يحلل البيانات..."):
            try:
                # تحضير السياق (Context)
                context = ""
                if uploaded_file:
                    file_text = get_pdf_text(uploaded_file)
                    context = f"المعلومات التالية مستخرجة من ملف مرفوع: {file_text[:5000]}\n\n" # نأخذ أول 5000 حرف
                
                # إعداد التعليمات حسب اللغة المختارة
                system_instruction = f"أنت مستشار استراتيجي ذكي يدعى تيجو. أجب باللغة {language} فقط. "
                if context:
                    system_instruction += "استخدم المعلومات الموجودة في الملف المرفوع للإجابة إذا كانت مرتبطة بالسؤال."
                
                # إرسال السؤال مع السياق
                full_prompt = f"{system_instruction}\n\nالسؤال: {prompt}"
                response = model.generate_content(full_prompt)
                
                full_response = response.text
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"حدث خطأ: {e}")