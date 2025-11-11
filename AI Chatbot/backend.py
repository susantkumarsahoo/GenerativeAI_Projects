"""
FastAPI Backend with LangChain + OpenAI
Run: python backend.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_classic.schema import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Chatbot API", version="1.0")



# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI with LangChain
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Request and Response Models
class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []

class ChatResponse(BaseModel):
    response: str
    success: bool


# Health check endpoint
@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Chatbot API",
        "version": "1.0"
    }
    
# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat messages with conversation history
    """
    try:
        # Build message list for LangChain
        messages = []
        
        # System prompt
        messages.append(
            SystemMessage(content="You are a helpful and friendly AI assistant.")
        )
        
        # Add conversation history
        for msg in request.conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Add current user message
        messages.append(HumanMessage(content=request.message))
        
        # Get AI response from OpenAI via LangChain
        ai_response = llm.invoke(messages)
        
        return ChatResponse(
            response=ai_response.content,
            success=True
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


# Run the server
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    print(f"🚀 Starting FastAPI server on port {port}...")
    uvicorn.run(app, host="127.0.0.1", port=port)




















