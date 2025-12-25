import streamlit as st
import base64
import os
from PyPDF2 import PdfReader
from huggingface_hub import InferenceClient

# --- 1. إعدادات الهوية والواجهة الفخمة ---
st.set_page_config(page_title="Tego AI Strategic Advisor", layout="wide")

# وظيفة لإظهار صورتك الشخصية بجانب رد تيجو لضمان ظهورها دائماً
def get_avatar_base64():
    if os.path.exists("me.jpg"):
        with open("me.jpg", "rb") as f:
            data = base64.b64encode(f.read()).decode()
            return f"data:image/jpeg;base64,{data}"
    return None

AVATAR = get_avatar_base64()

# --- 2. محرك الذكاء السحابي (بدون تثبيت برامج) ---
# الصق المفتاح الذي نسخته من Hugging Face هنا مكان النجوم أدناه
HF_TOKEN = "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" 
client = InferenceClient(api_key=HF_TOKEN)

def ask_tego_online(prompt, context):
    messages = [
        {"role": "system", "content": f"أنت تيجو، المستشار الاستراتيجي لطارق. استخدم هذه المعلومات المرفوعة للرد بذكاء: {context}"},
        {"role": "user", "content": prompt}
    ]
    try:
        # اتصال فوري وسريع عبر الإنترنت مثل Gemini
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct",
            messages=messages,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"تيجو: أستاذ طارق، يرجى التأكد من وضع مفتاح Token الصحيح في الكود. (Error: {str(e)})"

# --- 3. مركز تعلم تيجو (القائمة الجانبية) ---
with st.sidebar:
    st.markdown("### 🧠 مركز تعلم تيجو")
    # مكان رفع الملفات كما طلبت في صورك السابقة
    uploaded_file = st.file_uploader("ارفع (PDF) ليتعلم تيجو سحابياً:", type=['pdf'])
    
    if uploaded_file:
        with st.spinner("تيجو يقرأ ويستوعب الملف..."):
            reader = PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in reader.pages])
            st.session_state.pdf_info = text[:4000] # حفظ المعلومات في الذاكرة
            st.success("تم الاستيعاب! تيجو جاهز للرد بناءً على ملفك.")
    
    if st.button("مسح الذاكرة 🗑️"):
        st.session_state.pdf_info = ""
        st.session_state.messages = []
        st.rerun()

# --- 4. منطقة المحادثة التفاعلية ---
st.title("Tego AI Strategic Advisor")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة مع صورتك الشخصية
for msg in st.session_state.messages:
    current_avatar = AVATAR if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=current_avatar):
        st.markdown(msg["content"])

# استقبال سؤال طارق
if prompt := st.chat_input("تحدث مع تيجو بذكاء السحابة..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR):
        # سحب البيانات من "مركز التعلم" إذا كانت متوفرة
        context_data = st.session_state.get('pdf_info', "لا توجد ملفات مرفوعة حالياً")
        answer = ask_tego_online(prompt, context_data)
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})