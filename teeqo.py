import streamlit as st
import requests
import os
import base64
from PyPDF2 import PdfReader

# --- 1. الإعدادات والملفات ---
API_KEY = "AIzaSyAaixKmeK3og1N2MfZkoLt15JQyFSwdNKY"
MEMORY_FILE = "tego_final_memory.txt"
IMAGE_PATH = "me.jpg"  # تأكد من وضع صورتك بهذا الاسم بجانب الكود

# إنشاء ملف الذاكرة إذا لم يكن موجوداً
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("أنت المساعد الذكي Tego، صديق وفي ومثقف.\n")

# وظيفة تحويل الصورة لتعمل كأيقونة (Avatar)
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    return None

MY_AVATAR = get_image_base64(IMAGE_PATH)

# --- 2. محرك الاتصال الذكي (اكتشاف الموديل والمسار) ---

def find_active_route():
    """يبحث عن أي موديل ومسار متاح في حسابك لتجنب الأخطاء"""
    versions = ["v1", "v1beta"]
    for ver in versions:
        list_url = f"https://generativelanguage.googleapis.com/{ver}/models?key={API_KEY}"
        try:
            res = requests.get(list_url, timeout=10).json()
            if 'models' in res:
                for m in res['models']:
                    # نختار الموديل الذي يدعم توليد النصوص
                    if "generateContent" in m.get('supportedGenerationMethods', []):
                        return f"https://generativelanguage.googleapis.com/{ver}/{m['name']}:generateContent?key={API_KEY}"
        except:
            continue
    return None

def ask_tego(question):
    target_url = find_active_route()
    
    if not target_url:
        return "❌ خطأ: لم أتمكن من العثور على أي موديل مفعّل في حسابك. تأكد من تفعيل API في Google Cloud."

    # جلب السياق من الذاكرة (آخر 3000 حرف لضمان استقرار الطلب)
    context = ""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            context = f.read()[-3000:]

    payload = {
        "contents": [{
            "parts": [{"text": f"الذاكرة التاريخية:\n{context}\n\nسؤال المستخدم الحالي: {question}\nأجب كـ Tego:"}]
        }]
    }

    try:
        response = requests.post(target_url, json=payload, timeout=25)
        res_data = response.json()
        if response.status_code == 200:
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ جوجل ترفض الطلب: {res_data.get('error', {}).get('message')}"
    except Exception as e:
        return f"⚠️ حدث عطل فني: {str(e)}"

# --- 3. واجهة المستخدم (Streamlit) ---

st.set_page_config(page_title="Tego AI Global", layout="centered")

# الهيدر العلوي
header_col1, header_col2 = st.columns([1, 5])
with header_col1:
    if MY_AVATAR:
        st.markdown(f'<img src="{MY_AVATAR}" style="width:80px; height:80px; border-radius:50%; object-fit:cover; border:2px solid #007bff;">', unsafe_allow_html=True)
with header_col2:
    st.title("Tego AI Assistant")
    st.caption("النسخة الشاملة للتعلم العميق من الملفات")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة
for msg in st.session_state.messages:
    avatar = MY_AVATAR if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# إدخال الدردشة
if prompt := st.chat_input("تحدث مع Tego أو ارفع ملفاً ليتعلمه..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=MY_AVATAR):
        with st.spinner("Tego يراجع الملفات والذاكرة..."):
            answer = ask_tego(prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 4. القائمة الجانبية (مركز التحكم) ---

with st.sidebar:
    if MY_AVATAR:
        st.markdown(f'<center><img src="{MY_AVATAR}" style="width:130px; border-radius:20px; box-shadow: 2px 2px 15px rgba(0,0,0,0.2);"></center>', unsafe_allow_html=True)
    
    st.header("🧠 أرشفة المعلومات")
    
    uploaded_file = st.file_uploader("ارفع ملف (PDF أو TXT):", type=['txt', 'pdf'])
    if uploaded_file and st.button("بدء عملية التعلم"):
        text = ""
        try:
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text += page.extract_text()
            else:
                text = uploaded_file.getvalue().decode("utf-8")
            
            with open(MEMORY_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n[بيانات ملف {uploaded_file.name}]:\n{text}\n")
            st.success(f"تم بنجاح! Tego الآن يعرف محتويات {uploaded_file.name}")
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {e}")

    st.divider()
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

    if st.button("🔥 تصفير الذاكرة الدائمة"):
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
            st.success("تم مسح كل المعلومات المخزنة.")
            st.rerun()