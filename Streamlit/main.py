from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

# Postavi API ključ
API_KEY = "AIzaSyBC8XlF0rto7pKLFt-fQq_lO0RXiitXUfs"  # <-- OBAVEZNO unesi svoj API ključ ovdje
genai.configure(api_key=API_KEY)

# Inicijalizacija FastAPI aplikacije
app = FastAPI()

# Klasa za unos podataka u POST zahtjevu
class ChatRequest(BaseModel):
    messages: list  # Lista poruka u obliku [{"role": "user", "content": "tekst"}]

@app.post("/chat/")
async def chat(request: ChatRequest):
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="Message list cannot be empty")

        # Ako nema poruke koja traži odgovor na hrvatskom, dodaj automatski
        if not any("hrvatskom jeziku" in msg.get("content", "").lower() for msg in request.messages):
            request.messages.insert(0, {
                "role": "user",
                "content": "Od sada odgovaraj isključivo na hrvatskom jeziku."
            })

        # Konverzija poruka u format koji Gemini API očekuje
        gemini_messages = [
            {"role": msg["role"], "parts": [msg["content"]]}
            for msg in request.messages
        ]

        # Inicijalizacija modela i započinjanje razgovora s poviješću
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat(history=gemini_messages)

        # Slanje posljednje korisničke poruke
        response = chat.send_message(gemini_messages[-1]["parts"][0])

        # Vraćanje odgovora
        return {"response": response.text}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))