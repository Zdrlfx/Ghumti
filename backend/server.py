from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from inference import get_model_response
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Store conversation history for each session
conversation_history = []

# Request Model
class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "Ghumti Bus Assistant API is running!"}

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        # Get model response
        response = get_model_response(request.message, conversation_history)
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))