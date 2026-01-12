import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# --- إعدادات الواجهة ---
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية (تأكد أن الملف اسمه me.png بجانب الكود)
USER_IMAGE = "me.png"

# --- [ المكان المخصص للمفتاح ] ---
# استبدل النجوم بمفتاحك الذي حصلت عليه من Google AI Studio
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"
# ---------------------------------

# تهيئة الاتصال بالذكاء الاصطناعي
def setup_teego():
    if not API_KEY or "ضـع" in API_KEY:
        return None
    try:
        genai.configure(api_key=API_KEY)
        # استخدام موديل فلاش لضمان السرعة وتجنب أخطاء 404
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None

model = setup_teego()

# وظيفة قراءة ملفات الـ PDF المرفوعة
def get_pdf_content(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("مركز تحكم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    
    st.write("---")
    # خيار اختيار اللغة
    language = st.radio("اختر لغة الحوار / Language:", ["العربية", "English"])
    
    st.write("---")
    # رفع الملفات
    uploaded_file = st.file_uploader("ارفع ملف PDF ليتعلمه تيجو", type=['pdf'])
    if uploaded_file:
        st.success("تم قراءة الملف بنجاح!")

st.title("Tego AI Strategic Advisor")

# --- إدارة المحادثة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة مع صورتك الشخصية
for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- استقبال سؤالك والرد عليه ---
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    # إضافة سؤالك للسجل
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد الرد
    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if not model:
            st.error("⚠️ المفتاح غير صحيح أو لم يتم وضعه. يرجى التأكد من السطر رقم 17 في الكود.")
        else:
            with st.spinner("تيجو يحلل البيانات..."):
                try:
                    # دمج محتوى الملف إذا وجد
                    file_context = ""
                    if uploaded_file:
                        content = get_pdf_content(uploaded_file)
                        file_context = f"\nالمعلومات من الملف المرفوع: {content[:8000]}"
                    
                    # صياغة الطلب للذكاء الاصطناعي
                    full_prompt = f"أنت تيجو، مستشار استراتيجي ذكي. لغتك الحالية هي {language}. {file_context}\nالسؤال: {prompt}"
                    
                    response = model.generate_content(full_prompt)
                    answer = response.text
                    
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")