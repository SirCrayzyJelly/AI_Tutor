from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

# Inicijalizacija FastAPI aplikacije
app = FastAPI()

# Klijent za komunikaciju s Gemini API-jem
client = genai.Client(api_key="")

# Klasa za unos podataka u POST zahtjevu
class ChatRequest(BaseModel):
    message: str

@app.post("/chat/")
async def chat(request: ChatRequest):
    try:
        # Slanje zahtjeva prema Gemini API-u
        response = client.models.generate_content(
            model="gemini-1.5-flash", contents=request.message
        )
        # Vraćanje odgovora korisniku
        return {"response": response.text}
    except Exception as e:
        # Obrada greške
        raise HTTPException(status_code=400, detail=str(e))

