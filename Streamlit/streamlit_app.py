import streamlit as st
import requests

# Streamlit aplikacija
st.set_page_config(page_title="AI Tutor", page_icon="🤖")
st.title("🎓 AI Tutor - Your Personal Learning Assistant")
st.markdown("Ask any educational question and get AI-powered answers!")

# Chat input: Korisnik unosi pitanje
user_input = st.text_input("Ask your question...")

# Kada korisnik pritisne Enter i unese poruku
if user_input:
    try:
        # Pošaljemo POST zahtjev na naš FastAPI server
        payload = {"message": user_input}
        
        # Post zahtjev prema FastAPI backendu
        response = requests.post("http://127.0.0.1:8000/chat/", json=payload)
        
        # Provjeravamo status odgovora
        if response.status_code == 200:
            ai_response = response.json().get('response', 'No response from AI')
            st.write(f"**Your Question:** {user_input}")
            st.write(f"**AI Response:** {ai_response}")
        else:
            error_message = response.json().get('detail', 'Unknown error')
            st.error(f"Error: {error_message}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {str(e)}")
