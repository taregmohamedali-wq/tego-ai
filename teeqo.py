import streamlit as st
import requests
import os
import base64
import time
from PyPDF2 import PdfReader

# --- 1. الإعدادات الأساسية ---
API_KEY = "AIzaSyA29ifogr_JsHRKpXIy9IimSR9MWTwYgg0"
MEMORY_FILE = "tego_final_memory.txt"
IMAGE_PATH = "me.jpg" 

# إنشاء ملف الذاكرة إذا لم يكن موجوداً
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("أنا Tego، مساعدك الشخصي الذكي.\n")

# تحويل الصورة الشخصية لتظهر في الدردشة
def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
        except: return None
    return None

MY_AVATAR = get_image_base64(IMAGE_PATH)

# --- 2. محرك اكتشاف الموديلات التلقائي (حل مشكلة Not Found) ---

def find_active_model():
    """هذه الوظيفة تكتشف الموديل المتاح في حسابك تلقائياً"""
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        response = requests.get(list_url, timeout=10)
        if response.status_code == 200:
            models_list = response.json().get('models', [])
            # نبحث أولاً عن gemini-1.5-flash كخيار أول
            for m in models_list:
                if "gemini-1.5-flash" in m['name']:
                    return m['name']
            # إذا لم يوجد، نأخذ أول موديل يدعم توليد المحتوى
            for m in models_list:
                if "generateContent" in m.get('supportedGenerationMethods', []):
                    return m['name']
    except:
        pass
    return "models/gemini-1.5-flash" # خيار افتراضي أخيرة

def ask_tego(question):
    # اكتشاف الموديل الشغال حالياً
    active_model = find_active_model()
    url = f"https://generativelanguage.googleapis.com/v1beta/{active_model}:generateContent?key={API_KEY}"
    
    # جلب سياق الذاكرة
    context = ""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            context = f.read()[-1500:] 

    payload = {
        "contents": [{"parts": [{"text": f"الذاكرة: {context}\nالمستخدم: {question}\nرد كشخصية Tego بذكاء:"}]}]
    }

    try:
        response = requests.post(url, json=payload, timeout=25)
        res_data = response.json()
        
        if response.status_code == 200:
            return res_data['candidates'][0]['content']['parts'][0]['text']
        elif response.status_code == 429:
            return "⚠️ ضغط كبير على جوجل. انتظر دقيقة ثم حاول مرة أخرى."
        else:
            return f"❌ خطأ من جوجل: {res_data.get('error', {}).get('message')}"
    except Exception as e:
        return f"⚠️ عطل في الاتصال: {str(e)}"

# --- 3. تصميم الواجهة الرسومية (موبايل + كمبيوتر) ---

st.set_page_config(page_title="Tego AI Global", layout="centered")

# الهيدر (صورتك واسمك)
h_col1, h_col2 = st.columns([1, 4])
with h_col1:
    if MY_AVATAR:
        st.markdown(f'<img src="{MY_AVATAR}" style="width:75px; height:75px; border-radius:50%; object-fit:cover; border:2px solid #007bff;">', unsafe_allow_html=True)
with h_col2:
    st.title("Tego AI")
    st.caption("انا هنا لمساعدتك والتنظير معك")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=MY_AVATAR if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

# إدخال الدردشة
if prompt := st.chat_input("بماذا يمكنني مساعدتك؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=MY_AVATAR):
        with st.spinner("Tego يراجع النظام ويجيب..."):
            # نظام تبريد بسيط لمنع الحظر
            time.sleep(1)
            answer = ask_tego(prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 4. إدارة الذاكرة والملفات في القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ إدارة الذاكرة")
    uploaded_file = st.file_uploader("ارفع ملف للتعلم منه (PDF/TXT):", type=['txt', 'pdf'])
    
    if uploaded_file and st.button("تحديث ذاكرة تيجو"):
        text = ""
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages: text += page.extract_text()
        else:
            text = uploaded_file.getvalue().decode("utf-8")
        
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[بيانات ملف {uploaded_file.name}]:\n{text}\n")
        st.success("تم تحديث الذاكرة بنجاح!")
    
    st.divider()
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()