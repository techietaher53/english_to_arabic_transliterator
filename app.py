import streamlit as st
import csv
import re
import io
import base64
import os
import hashlib
from datetime import datetime

# ---- Load font from .ttf file and inject into app ----
def load_custom_font(font_path, font_name):
    with open(font_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    return f"""
    <style>
    @font-face {{
        font-family: '{font_name}';
        src: url(data:font/ttf;base64,{encoded}) format('truetype');
    }}
    .arabic-output {{
        font-family: '{font_name}', sans-serif;
        font-size: 24px;
        direction: rtl;
        unicode-bidi: isolate;
        line-height: 2;
        white-space: pre-line;
        text-align: right;
    }}
    </style>
    """

# ---- Load transliteration dictionary ----
def load_transliteration_dict(csv_path="transliteration_dataset.csv"):
    translit_dict = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                eng = row[0].strip().lower()
                arb = row[1].strip()
                translit_dict[eng] = arb
    return translit_dict

# ---- Transliteration logic ----
def transliterate_sentence(sentence, translit_dict):
    lines = sentence.strip().split('\n')
    transliterated_lines = []

    for line in lines:
        words = line.strip().split()
        transliterated_words = []
        for word in words:
            key = word.lower()
            if key in translit_dict:
                transliterated_words.append(translit_dict[key])
            else:
                transliterated_words.append(word)
        transliterated_lines.append(" ".join(transliterated_words))

    return "\n".join(transliterated_lines)

# ---- Format output for Microsoft Word ----
def format_for_word_export(text):
    return f"<div dir='rtl' style='font-size:22px; line-height:2; font-family:Tahoma;'>\n{text.replace(chr(10), '<br>')}\n</div>"

# ---- Update dictionary from user input ----
def update_translit_dict_from_user(input_text, translit_dict, csv_path="transliteration_dataset.csv"):
    words = set(input_text.strip().lower().split())
    if "used_input_keys" not in st.session_state:
        st.session_state.used_input_keys = set()

    for word in words:
        if word not in translit_dict and re.match(r'^[a-zA-Z]+$', word):
            input_hash = hashlib.md5((word + input_text).encode()).hexdigest()[:6]
            input_key = f"missing-{word}-{input_hash}"

            if input_key in st.session_state.used_input_keys:
                continue

            st.session_state.used_input_keys.add(input_key)
            arabic = st.text_input(f"📝 Enter Arabic for: **{word}**", key=input_key)
            if arabic and f"saved-{word}" not in st.session_state:
                try:
                    translit_dict[word] = arabic
                    with open(csv_path, "a", encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([word, arabic])
                    st.session_state[f"saved-{word}"] = True
                    st.success(f"✅ Saved: `{word}` → `{arabic}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error writing to CSV: {e}")
    return translit_dict

# ---- Page configuration ----
st.set_page_config(page_title="📄 Word-Formatted Arabic Transliterator", layout="centered")
st.title("🔤 Arabic Transliterator — Word Compatible")

# ---- Sidebar: Font selector ----
st.sidebar.markdown("### 🔠 Font Settings")
selected_font = st.sidebar.selectbox("Choose Arabic Font", ["Al-Kanz", "Kanz-al-Marjaan"])
font_files = {
    "Al-Kanz": "Al-Kanz for Windows.ttf",
    "Kanz-al-Marjaan": "Kanz-al-Marjaan.ttf"
}
font_css = load_custom_font(font_files[selected_font], selected_font)
st.markdown(font_css, unsafe_allow_html=True)

# ---- Load dictionary and handle CSV reload ----
csv_path = "transliteration_dataset.csv"
translit_map = load_transliteration_dict(csv_path)

if st.sidebar.button("🔁 Reload CSV"):
    st.cache_data.clear()
    st.rerun()

# ---- Chat UI ----
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"```\n{msg['content']}\n```")

user_input = st.chat_input("Type your sentence here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"```\n{user_input}\n```")

    # Update dictionary with new words
    translit_map = update_translit_dict_from_user(user_input, translit_map, csv_path)

    # --- Special "Mubaraka" filter ---
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"```\n{user_input}\n```")

    translit_map = update_translit_dict_from_user(user_input, translit_map, csv_path)

    result = transliterate_sentence(user_input, translit_map)

    html_output = format_for_word_export(result)

    with st.chat_message("assistant"):
        st.markdown(html_output, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": result})

        result = transliterate_sentence(user_input, translit_map)

    # Format for Word
    html_output = format_for_word_export(result)

    with st.chat_message("assistant"):
        st.markdown(html_output, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": result})
