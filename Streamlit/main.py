from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai 

#Postavi API ključ
API_KEY = ""
genai.configure(api_key=API_KEY)

#Inicijalizacija FastAPI aplikacije
app = FastAPI()

#Klasa za unos podataka u POST zahtjevu
class ChatRequest(BaseModel):
    messages: list  #Lista poruka za pamćenje razgovora

@app.post("/chat/")
async def chat(request: ChatRequest):
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="Message list cannot be empty")

        #Koristimo model
        model = genai.GenerativeModel("gemini-1.5-flash")

        #Slanje razgovora modelu
        response = model.generate_content(request.messages[-1]["content"])

        return {"response": response.text}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
