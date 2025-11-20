import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Anime Character Chatbot API")

# Enable CORS for local development and preview hosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In dev, allow all. In prod, lock this down.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    character: str = Field(..., description="Selected anime character")
    message: str = Field(..., description="User message")


class ChatResponse(BaseModel):
    reply: str


# Persona templates
LEVI_PREFIX = (
    "Tch… "
)
GOJO_PREFIX = (
    "Heyyy! "
)


def generate_persona_reply(character: str, message: str) -> str:
    name = character.strip().lower()

    if "levi" in name:
        # Short, serious, curt
        if not message.strip():
            return "Tch… Speak clearly. What do you want?"
        return f"Tch… {message.strip().capitalize()}? Keep it brief. I don't have time for fluff."

    if "gojo" in name or "satoru" in name:
        # Energetic, confident, playful
        if not message.strip():
            return "Heyyy! What’s up? I'm all ears!"
        return (
            "Heyyy! "
            + f"{message.strip().capitalize()} — love the energy! Don't worry, I've got this. 😎"
        )

    # Default fallback if unknown character
    if not message.strip():
        return "Hello! Pick a character and say something."
    return f"You said: '{message.strip()}'. Choose Levi or Satoru Gojo for a styled reply."


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.character:
        raise HTTPException(status_code=400, detail="Character is required")
    reply = generate_persona_reply(req.character, req.message)
    return ChatResponse(reply=reply)


@app.get("/")
def read_root():
    return {"message": "Anime Character Chatbot Backend running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
