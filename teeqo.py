import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# --- [ المكان المحدد للمفتاح ] ---
# ضع مفتاحك هنا بدلاً من الكلمة المكتوبة
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"
# -------------------------------

# 2. وظيفة الربط الذكي لتجنب أخطاء 404 و 400
def initialize_teego():
    if not API_KEY or "ضـع" in API_KEY:
        return None
    try:
        # تنظيف المفتاح من أي مسافات زائدة قد تسبب خطأ 400
        genai.configure(api_key=API_KEY.strip())
        
        # فحص الموديلات المتاحة في حسابك واختيار الشغال منها تلقائياً
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # محاولة اختيار أفضل موديل متاح (فلاش أو برو)
        if 'models/gemini-1.5-flash' in models:
            return genai.GenerativeModel('gemini-1.5-flash')
        elif 'models/gemini-pro' in models:
            return genai.GenerativeModel('gemini-pro')
        elif models:
            return genai.GenerativeModel(models[0])
        return None
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
        return None

model = initialize_teego()

# 3. القائمة الجانبية (اللغة + الملفات)
with st.sidebar:
    st.title("مركز تحكم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    
    # خيار اللغة (العربية أو الإنجليزية)
    lang = st.radio("لغة الرد / Language:", ["العربية", "English"])
    
    st.write("---")
    # رفع ملفات PDF للتحليل
    uploaded_file = st.file_uploader("ارفع ملف PDF ليتعلمه تيجو", type=['pdf'])

# 4. سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. معالجة السؤال (من الملف أو الإنترنت)
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if not model:
            st.warning("⚠️ النظام غير متصل. تأكد من وضع المفتاح الصحيح في السطر 15.")
        else:
            with st.spinner("تيجو يحلل ويجيب..."):
                try:
                    # استخراج النص من الملف إذا تم رفعه
                    context = ""
                    if uploaded_file:
                        reader = PdfReader(uploaded_file)
                        text = "".join([page.extract_text() for page in reader.pages])
                        context = f"معلومات من الملف المرفوع: {text[:8000]}\n\n"
                    
                    # صياغة الطلب مع اللغة المختارة
                    full_query = f"أنت تيجو، مستشار استراتيجي ذكي. لغتك الحالية هي {lang}. {context} السؤال: {prompt}"
                    response = model.generate_content(full_query)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"حدث خطأ أثناء المعالجة: {e}")