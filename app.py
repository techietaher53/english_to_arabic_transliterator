import streamlit as st
import csv

# ---- Load CSV into dictionary ----
@st.cache_data
def load_transliteration_dict(csv_path):
    translit_dict = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                eng = row[0].strip().lower()
                arb = row[1].strip()
                translit_dict[eng] = arb
    return translit_dict

translit_map = load_transliteration_dict("transliteration_dataset.csv")
if st.sidebar.button("🔁 Reload CSV"):
    st.cache_data.clear()
    st.rerun()


# ---- Transliterate full sentence ----
def transliterate_sentence(sentence, translit_dict):
    words = sentence.strip().lower().split()
    transliterated_words = []

    for word in words:
        arabic = translit_dict.get(word, f"[{word}]")  # show fallback in brackets
        transliterated_words.append(arabic)

    return " ".join(transliterated_words)

# ---- Streamlit UI ----
st.set_page_config(page_title="🗣️ Transliteration Bot", layout="centered")
st.title("🗣️ English-Arabic Transliteration Chatbot")
st.write("Type any English-transliterated sentence (like `khabar karwa ma che`) and get the Arabic transliteration.")

# ---- Chat Logic ----
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your sentence here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get transliteration result
    result = transliterate_sentence(user_input, translit_map)

    with st.chat_message("assistant"):
        st.markdown(result)
        st.session_state.messages.append({"role": "assistant", "content": result})
import streamlit as st