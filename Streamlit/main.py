from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import sys
import os
from Backend.vektorizacija import qa_base


# Omogući pristup mapi Backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend")))

# Postavi API ključ
API_KEY = ""  # <-- OBAVEZNO unesi svoj API ključ ovdje
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

        # Posljednje korisničko pitanje
        user_input = request.messages[-1]["content"]

        # Prvo pokušaj odgovoriti preko FAISS baze
        response_from_base = qa_base.search(user_input, top_k=1, threshold=0.75)
        if response_from_base:
            return {"response": response_from_base}

        # Ako nije pronađen odgovor, koristi Gemini
        if not any("hrvatskom jeziku" in msg.get("content", "").lower() for msg in request.messages):
            request.messages.insert(0, {
                "role": "user",
                "content": "Od sada odgovaraj isključivo na hrvatskom jeziku."
            })

        gemini_messages = [
            {"role": msg["role"], "parts": [msg["content"]]}
            for msg in request.messages
        ]

        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat(history=gemini_messages)
        response = chat.send_message(gemini_messages[-1]["parts"][0])

        return {"response": response.text}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))