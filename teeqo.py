import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# 1. إعدادات الصفحة والواجهة
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# --- [ضع مفتاحك هنا بدقة بين علامتي التنصيص] ---
API_KEY = "ضـع_مفتاحـك_هنـا"
# ---------------------------------------------

# 2. تهيئة الموديل مع فحص تلقائي لتجنب خطأ 404
def initialize_smart_model():
    if not API_KEY or API_KEY == "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA":
        return None
    try:
        genai.configure(api_key=API_KEY)
        # فحص الموديلات المتاحة في حسابك واختيار الأفضل
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if 'models/gemini-1.5-flash' in available_models:
            return genai.GenerativeModel('gemini-1.5-flash')
        elif 'models/gemini-pro' in available_models:
            return genai.GenerativeModel('gemini-pro')
        return genai.GenerativeModel(available_models[0])
    except:
        return None

model = initialize_smart_model()

# 3. وظيفة قراءة ملفات الـ PDF
def read_pdf(file):
    pdf_reader = PdfReader(file)
    content = ""
    for page in pdf_reader.pages:
        content += page.extract_text()
    return content

# 4. القائمة الجانبية (اللغة + الملفات)
with st.sidebar:
    st.title("مركز تحكم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    
    # خيار اللغة
    lang = st.radio("لغة الحوار / Language", ["العربية", "English"])
    
    st.write("---")
    # رفع الملف
    uploaded_file = st.file_uploader("ارفع ملف استراتيجي (PDF)", type=['pdf'])
    if uploaded_file:
        st.success("تم رفع الملف بنجاح!")

st.title("Tego AI Strategic Advisor")

# 5. إدارة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة (صورتك تظهر كأفاتار لتيجو)
for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 6. استقبال السؤال وتوليد الإجابة الذكية
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    # إضافة سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد رد تيجو
    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if not model:
            st.error("المفتاح غير صحيح أو غير موجود. يرجى وضعه في الكود.")
        else:
            with st.spinner("تيجو يحلل البيانات..."):
                try:
                    # بناء السياق (إذا كان هناك ملف مرفوع)
                    file_context = ""
                    if uploaded_file:
                        file_context = f"\nالمعلومات من الملف: {read_pdf(uploaded_file)[:4000]}"
                    
                    # التعليمات البرمجية (System Prompt)
                    system_prompt = f"أنت تيجو، مستشار استراتيجي ذكي. لغتك الحالية هي {lang}. "
                    if file_context:
                        system_prompt += "استخدم بيانات الملف المرفوع للإجابة بدقة."
                    
                    # طلب الرد
                    full_query = f"{system_prompt}\n\nالسؤال: {prompt}\n{file_context}"
                    response = model.generate_content(full_query)
                    
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"حدث خطأ أثناء المعالجة: {e}")