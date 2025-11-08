import streamlit as st
import requests

st.set_page_config(page_title="LangChain Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 LangChain + FastAPI Chatbot")

# Backend URL
API_URL = "http://127.0.0.1:8000/chat"

# Chat state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat UI
for msg in st.session_state.messages:
    role = "🧑‍💻 You" if msg["is_user"] else "🤖 Bot"
    st.markdown(f"**{role}:** {msg['text']}")

user_input = st.text_input("Type your message:", key="input")

if st.button("Send") and user_input:
    # Add user message
    st.session_state.messages.append({"text": user_input, "is_user": True})

    # Send to backend
    with st.spinner("Thinking..."):
        res = requests.post(API_URL, json={"message": user_input})
        bot_reply = res.json().get("response", "Error")

    # Add bot message
    st.session_state.messages.append({"text": bot_reply, "is_user": False})
    st.experimental_rerun()

        
        
