import streamlit as st
import ollama
from PyPDF2 import PdfReader
import base64
import os
import requests
from bs4 import BeautifulSoup
import re

# ----------------------------------
# إعداد الصفحة
# ----------------------------------
st.set_page_config(page_title="Tego AI Agent", layout="wide")
st.title(" Tego  Agent ")
st.caption("Agent محلي • عربي واضح • إنترنت ذكي • بدون API")

# ----------------------------------
# Avatar
# ----------------------------------
def load_avatar():
    if os.path.exists("avatar.png"):
        with open("avatar.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

AVATAR = load_avatar()

# ----------------------------------
# الحالة
# ----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# ----------------------------------
# Sidebar
# ----------------------------------
with st.sidebar:
    st.header("📂 مركز المعرفة")

    uploaded_file = st.file_uploader("ارفع PDF (اختياري)", type=["pdf"])
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text = ""
        for p in reader.pages:
            if p.extract_text():
                text += p.extract_text()
        st.session_state.pdf_context = text[:1200]
        st.success("تم تحميل الملف")

    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.messages = []
        st.session_state.pdf_context = ""
        st.rerun()

# ----------------------------------
# 🌐 بحث إنترنت نظيف
# ----------------------------------
def web_search_clean(query):
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text[:1200]
    except:
        return ""

# ----------------------------------
# 🧠 قرار استخدام الإنترنت
# ----------------------------------
def should_use_internet(prompt):
    keywords = ["سعر", "اليوم", "الآن", "آخر", "حديث", "أخبار", "كم"]
    return any(word in prompt for word in keywords)

# ----------------------------------
# 🧠 Agent الرئيسي (عربي نظيف)
# ----------------------------------
def ask_tego(prompt, context):
    internet_data = ""
    if should_use_internet(prompt):
        internet_data = web_search_clean(prompt)

    system_prompt = f"""
أنت مساعد ذكي عربي اسمه تيجو.

التزم بالقواعد التالية حرفيًا:
- اكتب بالعربية فقط
- جمل واضحة وقصيرة
- لا تكتب أي تفكير داخلي
- لا تخلط لغات
- إذا كانت المعلومة غير مؤكدة، اذكر ذلك بوضوح

معلومات إضافية:
{context}

معلومات من الإنترنت:
{internet_data}
"""

    response = ollama.chat(
        model="gemma:2b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        options={"num_predict": 160}
    )

    return response["message"]["content"]

# ----------------------------------
# عرض المحادثة
# ----------------------------------
for msg in st.session_state.messages:
    avatar = f"data:image/png;base64,{AVATAR}" if msg["role"] == "assistant" and AVATAR else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ----------------------------------
# إدخال المستخدم
# ----------------------------------
user_input = st.chat_input("تحدث مع تيجو...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=f"data:image/png;base64,{AVATAR}" if AVATAR else None):
        with st.spinner("تيجو يجيب..."):
            answer = ask_tego(user_input, st.session_state.pdf_context)
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
