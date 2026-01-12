import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية (تأكد أن الملف بنفس الاسم me.png بجانب الكود)
USER_IMAGE = "me.png"

# --- [ المكان المخصص للمفتاح - ضع كود API هنا ] ---
# انسخ مفتاحك من Google AI Studio وضعه هنا بدقة بين علامتي التنصيص
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"
# -----------------------------------------------

# 2. تهيئة الاتصال الذكي (حل مشكلة 404 و 400)
def initialize_teego():
    if not API_KEY or "ضـع" in API_KEY:
        return None
    try:
        genai.configure(api_key=API_KEY)
        # فحص الموديلات المتاحة واختيار المتاح منها تلقائياً
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available else 'models/gemini-pro'
        return genai.GenerativeModel(target)
    except Exception as e:
        return None

model = initialize_teego()

# 3. وظيفة قراءة ملفات الـ PDF
def read_pdf(file):
    reader = PdfReader(file)
    content = ""
    for page in reader.pages:
        content += page.extract_text()
    return content

# 4. القائمة الجانبية (اللغة والملفات)
with st.sidebar:
    st.title("مركز تحكم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    
    st.write("---")
    language = st.radio("اختر لغة الحوار / Language:", ["العربية", "English"])
    
    st.write("---")
    uploaded_file = st.file_uploader("ارفع ملف PDF ليتعلمه تيجو", type=['pdf'])
    if uploaded_file:
        st.success("تم تحليل الملف")

st.title("Tego AI Strategic Advisor")

# 5. سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة مع صورتك
for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 6. معالجة السؤال والرد
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if not model:
            st.error("⚠️ المفتاح غير صحيح أو لم يتم وضعه في السطر 18.")
        else:
            with st.spinner("تيجو يحلل ويجيب..."):
                try:
                    # سياق الملف المرفوع
                    context = ""
                    if uploaded_file:
                        pdf_text = read_pdf(uploaded_file)
                        context = f"معلومات من الملف: {pdf_text[:8000]}\n\n"
                    
                    # صياغة الطلب
                    full_query = f"أنت تيجو، مستشار استراتيجي. أجب بـ {language}. {context} السؤال: {prompt}"
                    response = model.generate_content(full_query)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")