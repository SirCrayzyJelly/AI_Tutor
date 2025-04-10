import streamlit as st
import requests

#Inicijalizacija Streamlit aplikacije
st.set_page_config(page_title="AI Tutor", page_icon="🤖")
st.title("🎓 AI Tutor - Tvoj virtualni prijatelj za učenje!")
st.markdown("Nema pitanja na koja AI ne zna odgovor! Postavi pitanje i učimo zajedno.")

#Inicijalizacija chat povijesti ako ne postoji
#Iteracija kroz sve poruke koje su pohranjene u povijesti razgovora (chat_history)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

#Ovisno o ulozi poruke(korisnik ili asistent), prikazujemo u odgovarajućem formatu
#"role" moze biti "user" ili "assistent" i određuje tko je poslao poruku
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):

        #Ispisuj sadrzaj poruke (pitanje ili odgovor)
        st.write(message["content"])

#Unos korisničkog pitanja
#Kada korisnik unese pitanje u chat, to se pitanje odmah obradi
if user_input := st.chat_input("Postavi svoje pitanje..."):
    # Dodaj korisničku poruku u povijest(chat_history)
    #Kreiramo novi objekt koji sadrži ulogu "user" i korisničko pitanje
    user_msg = {"role": "user", "content": user_input}

    #Pohrani korisničko pitanje u chat_history kako bi se pratila povijest razgovora
    st.session_state.chat_history.append(user_msg)

    #Korisničko pitanje prikazujemo na ekranu i odgovarajuću ulogu
    with st.chat_message("user"):
        st.write(user_input)

    # Pripremi povijest svih poruka (korisnikovih i asistetovih koristeci odgovarajucu ulogu)
    payload = {"messages": st.session_state.chat_history}

    try:
        #Pošalji POST zahtjev na backend s chat_history kako bi AI generirao odgovor
        response = requests.post("http://127.0.0.1:8000/chat/", json=payload)


        #Ako je odgovor od backenda uspješan, preuzmi odgovor od AI-a
        if response.status_code == 200:
            ai_response = response.json().get("response", "No response from AI")

            #Dodaj AI odgovor u chat_history kako bi mogao biti prikazan poslije
            assistant_msg = {"role": "assistant", "content": ai_response}
            st.session_state.chat_history.append(assistant_msg)

            #Prikaži AI odgovor 
            with st.chat_message("assistant"):
                st.write(ai_response)
        else:

            #Ako dođe do greške u backendu, prikaži korisniku grešku
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        #Ako dođe do greške u vezi sa povezivanjem sa backendom, prikaži je
        st.error(f"Error connecting to the backend: {str(e)}")
