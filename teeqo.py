import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# 1. إعدادات الصفحة والواجهة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية (تأكد أن الملف بنفس الاسم me.png بجانب الكود)
USER_IMAGE = "me.png"

# --- [ المكان المخصص للمفتاح - API KEY ] ---
# انسخ مفتاحك من Google AI Studio وضعه هنا بدقة
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"
# ------------------------------------------

# 2. تهيئة الاتصال الذكي وتجنب أخطاء 404
def initialize_teego():
    if not API_KEY or "ضـع" in API_KEY:
        return None
    try:
        genai.configure(api_key=API_KEY)
        # البحث عن أفضل موديل متاح في حسابك تلقائياً
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else 'models/gemini-pro'
        return genai.GenerativeModel(target)
    except Exception as e:
        st.error(f"خطأ في التهيئة: {e}")
        return None

model = initialize_teego()

# 3. وظيفة معالجة ملفات PDF
def read_pdf_file(file):
    try:
        reader = PdfReader(file)
        return "".join([page.extract_text() for page in reader.pages])
    except:
        return ""

# 4. القائمة الجانبية (Sidebar)
with st.sidebar:
    st.title("مركز تحكم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    
    st.write("---")
    # اختيار اللغة
    language = st.radio("اختر لغة الحوار / Language:", ["العربية", "English"])
    
    st.write("---")
    # رفع الملفات
    uploaded_file = st.file_uploader("ارفع ملف PDF ليتعلمه تيجو", type=['pdf'])
    if uploaded_file:
        st.success("✅ تم قراءة الملف بنجاح")

st.title("Tego AI Strategic Advisor")

# 5. إدارة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة مع صورتك الشخصية كأفاتار لتيجو
for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 6. استقبال السؤال وتوليد الرد الذكي
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if not model:
            st.error("⚠️ المفتاح (API Key) غير صحيح أو لم يتم وضعه في السطر 18.")
        else:
            with st.spinner("تيجو يحلل ويجيب..."):
                try:
                    # بناء السياق من الملف المرفوع
                    context = ""
                    if uploaded_file:
                        file_text = read_pdf_file(uploaded_file)
                        context = f"استخدم هذه المعلومات من الملف المرفوع للإجابة: {file_text[:8000]}\n\n"
                    
                    # صياغة الطلب النهائي
                    full_query = f"أنت تيجو، مستشار استراتيجي ذكي. لغتك الحالية: {language}. {context} السؤال: {prompt}"
                    response = model.generate_content(full_query)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"عذراً، حدث خطأ أثناء المعالجة: {e}")