import streamlit as st
import google.generativeai as genai
import os

# 1. إعدادات الصفحة والجمالية
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# مسار صورتك الشخصية
USER_IMAGE = "me.png"

# 2. إعداد المفتاح (تأكد من وضعه بدقة هنا)
API_KEY = "AIzaSyDRJ1MRnpBEnEN2ArpJ_j0Yvyh6pbroVWA"

def setup_model():
    if not API_KEY or API_KEY == "ضـع_مفتاحـك_هنـا":
        st.error("⚠️ الرجاء وضع مفتاح API صحيح داخل الكود.")
        return None
    
    try:
        genai.configure(api_key=API_KEY)
        # محاولة الاتصال بموديلات مختلفة لضمان العمل (حل مشكلة 404)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # ترتيب الأولويات: نجرب 1.5 فلاش، ثم 1.5 برو، ثم Gemini Pro القديم
        if 'models/gemini-1.5-flash' in available_models:
            return genai.GenerativeModel('gemini-1.5-flash')
        elif 'models/gemini-pro' in available_models:
            return genai.GenerativeModel('gemini-pro')
        else:
            # إذا لم نجد الأسماء السابقة، نستخدم أول موديل متاح
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"❌ فشل الاتصال بخدمة جوجل: {e}")
        return None

model = setup_model()

# 3. واجهة المستخدم (Sidebar)
with st.sidebar:
    st.title("مركز تعلم تيجو 🧠")
    if os.path.exists(USER_IMAGE):
        st.image(USER_IMAGE, width=120)
    st.write("(PDF) ارفع ملفاتك ليتعلم منها تيجو")
    st.file_uploader("اسحب الملف هنا", type=['pdf'])

st.title("Tego AI Strategic Advisor")

# 4. ذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة مع صورتك للردود
for message in st.session_state.messages:
    avatar = USER_IMAGE if message["role"] == "assistant" and os.path.exists(USER_IMAGE) else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. منطقة الإدخال والرد الذكي
if prompt := st.chat_input("تحدث مع تيجو بذكاء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=USER_IMAGE if os.path.exists(USER_IMAGE) else None):
        if model:
            try:
                with st.spinner("تيجو يحلل ويجيب..."):
                    # محاولة توليد الرد
                    response = model.generate_content(prompt)
                    if response.text:
                        full_response = response.text
                        st.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    else:
                        st.warning("الموديل استلم السؤال ولكن لم يستطع صياغة رد.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء التوليد: {e}")
        else:
            st.info("النظام بانتظار اتصال صحيح بالخادم.")