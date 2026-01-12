import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# 1. إعدادات الصفحة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# 2. إعداد المفتاح والموديل
# --- [ضع مفتاحك هنا بدقة] ---
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"
# ---------------------------

if API_KEY and API_KEY != "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA":
    try:
        genai.configure(api_key=API_KEY)
        # استخدام موديل مستقر يدعم اللغة العربية والملفات
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"خطأ في الاتصال بخدمة الذكاء الاصطناعي: {e}")
        model = None
else:
    model = None

# وظيفة استخراج النص من ملف PDF
def extract_pdf_content(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# 3. القائمة الجانبية (خيار اللغة وتحميل الملفات)
with st.sidebar:
    st.title("مركز تحكم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    
    # اختيار اللغة
    language = st.selectbox("لغة الحوار / Language:", ["العربية", "English"])
    
    st.write("---")
    st.write("📂 تحليل البيانات الاستراتيجية")
    uploaded_file = st.file_uploader("ارفع ملف PDF ليتعلمه تيجو", type=['pdf'])
    if uploaded_file:
        st.success("تم تحليل الملف بنجاح!")

st.title("Tego AI Strategic Advisor")

# 4. إدارة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة مع صورتك الشخصية
for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. معالجة السؤال والذكاء الاصطناعي
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if not model:
            st.error("الرجاء وضع مفتاح API صحيح في الكود.")
        else:
            with st.spinner("تيجو يحلل ويجيب..."):
                try:
                    # تحضير سياق الملف إذا وجد
                    context = ""
                    if uploaded_file:
                        pdf_text = extract_pdf_content(uploaded_file)
                        context = f"استخدم المعلومات التالية من الملف المرفوع للإجابة: {pdf_text[:10000]}\n\n"
                    
                    # صياغة التعليمات النهائية
                    system_prompt = f"أنت مستشار استراتيجي ذكي اسمك تيجو. أجب باللغة {language} فقط."
                    full_query = f"{system_prompt}\n{context}\nالسؤال: {prompt}"
                    
                    response = model.generate_content(full_query)
                    answer = response.text
                    
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"عذراً، حدث خطأ أثناء المعالجة: {e}")