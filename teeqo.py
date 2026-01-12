import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# 1. إعدادات الصفحة والجمالية
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# --- [ضع مفتاحك هنا بدقة] ---
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"
# ---------------------------

# 2. وظيفة الربط الذكي بالذكاء الاصطناعي
def get_working_model():
    if not API_KEY or API_KEY == "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA":
        return None
    try:
        genai.configure(api_key=API_KEY)
        # فحص الموديلات المتاحة لتجنب خطأ 404
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # محاولة اختيار أفضل موديل متاح
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else 'models/gemini-pro'
        return genai.GenerativeModel(target)
    except:
        return None

model = get_working_model()

# 3. القائمة الجانبية (اللغة والملفات)
with st.sidebar:
    st.title("مركز تحكم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    
    # اختيار اللغة
    language = st.radio("اختر لغة الحوار / Language:", ["العربية", "English"])
    
    st.write("---")
    st.write("📂 تحليل الملفات الاستراتيجية")
    uploaded_file = st.file_uploader("ارفع ملف PDF ليتعلمه تيجو", type=['pdf'])

# 4. إدارة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة مع صورتك الشخصية للردود
for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. استقبال السؤال ومعالجته (من الملف أو الإنترنت)
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if not model:
            st.error("❌ المفتاح غير صحيح أو غير موجود. يرجى التأكد من وضعه في الكود.")
        else:
            with st.spinner("تيجو يحلل ويجيب..."):
                try:
                    # جلب سياق من الملف المرفوع إذا وجد
                    context = ""
                    if uploaded_file:
                        reader = PdfReader(uploaded_file)
                        text = "".join([page.extract_text() for page in reader.pages])
                        context = f"المعلومات من الملف المرفوع: {text[:5000]}\n\n"
                    
                    # إرسال الاستعلام
                    full_query = f"أنت تيجو، مستشار استراتيجي. أجب باللغة {language}. {context} السؤال: {prompt}"
                    response = model.generate_content(full_query)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال: {e}")