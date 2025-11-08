from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://localhost:8501"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chat request model
class ChatRequest(BaseModel):
    message: str

# LangChain model
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = llm.invoke(request.message)
        return {"response": response.content}
    except Exception as e:
        return {"error": str(e)}
 

