# main.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationChain
from langchain_classic.prompts import PromptTemplate

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY. Please set it in .env file")

# Initialize FastAPI app
app = FastAPI(title="LangChain Chatbot", version="1.0")


# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangChain LLM setup
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.3,
    openai_api_key=OPENAI_API_KEY,
)

# In-memory store for session-based memory
MEMORY_STORE = {}


# Request/Response schema
class ChatRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    reply: str
    history: List[str]


def get_memory(session_id: str = "default"):
    """Return or create a memory buffer for each user/session"""
    if session_id not in MEMORY_STORE:
        MEMORY_STORE[session_id] = ConversationBufferMemory(return_messages=False)
    return MEMORY_STORE[session_id]

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main chatbot endpoint"""
    user_text = req.user_input.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty user_input")

    # Retrieve or create memory
    memory = get_memory(req.session_id)

    # Conversation chain
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template="{history}\nHuman: {input}\nAssistant:",
    )

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=False,
    )

    try:
        reply = conversation.run(input=user_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Format conversation history
    history_text = memory.buffer if hasattr(memory, "buffer") else ""
    history_lines = [line.strip() for line in history_text.split("\n") if line.strip()]

    return JSONResponse({"reply": reply, "history": history_lines})

@app.get("/", response_class=HTMLResponse)
async def serve_html(request: Request):
    """Serve the chatbot UI"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

































