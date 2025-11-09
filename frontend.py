"""
Streamlit Frontend for AI Chatbot
Run: streamlit run frontend.py
"""

import streamlit as st
import httpx
import time


# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .main {
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:8000/chat"


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_status" not in st.session_state:
    st.session_state.api_status = "unknown"
    
    
# Check API health
def check_api_health():
    try:
        response = httpx.get("http://localhost:8000/", timeout=5.0)
        if response.status_code == 200:
            return "online"
    except:
        pass
    return "offline"

# Main UI
st.title("💬 AI Chatbot")
st.caption("🚀 Powered by LangChain + OpenAI + FastAPI")


# Check API status
st.session_state.api_status = check_api_health()


if st.session_state.api_status == "offline":
    st.error("⚠️ Backend API is offline. Please start backend.py first!")
    st.code("python backend.py", language="bash")
    st.stop()



# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# Chat input
if user_input := st.chat_input("Type your message here..."):
    
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Show thinking indicator
            message_placeholder.markdown("🤔 Thinking...")
            
            # Prepare conversation history (exclude current message)
            history = st.session_state.messages[:-1]
            
            # Call backend API
            response = httpx.post(
                API_URL,
                json={
                    "message": user_input,
                    "conversation_history": history
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["response"]
                
                # Display AI response with typing effect
                full_response = ""
                for char in ai_response:
                    full_response += char
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)
                
                message_placeholder.markdown(ai_response)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })
            else:
                message_placeholder.error(f"❌ API Error: {response.status_code}")
                
        except httpx.ConnectError:
            message_placeholder.error("❌ Cannot connect to backend!")
        except httpx.TimeoutException:
            message_placeholder.error("❌ Request timeout!")
        except Exception as e:
            message_placeholder.error(f"❌ Error: {str(e)}")


# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Statistics
    st.subheader("📊 Statistics")
    total_messages = len(st.session_state.messages)
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    ai_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", total_messages)
    with col2:
        st.metric("Exchanges", user_messages)
    
    st.divider()
    
    # System info
    st.subheader("ℹ️ System Info")
    st.caption("**Status:** " + ("🟢 Online" if st.session_state.api_status == "online" else "🔴 Offline"))
    st.caption("**Backend:** FastAPI")
    st.caption("**Model:** GPT-3.5-turbo")
    st.caption("**Framework:** LangChain")
    
    st.divider()
    
    
    
        # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        1. Type your message in the chat input
        2. Press Enter to send
        3. Wait for AI response
        4. Continue the conversation
        5. Click 'Clear Chat' to reset
        """)
  
 
