import streamlit as st
from fpdf import FPDF
import requests

# Inicijalizacija Streamlit aplikacije
st.set_page_config(page_title="AI Tutor", page_icon="🤖")
st.title("🎓 AI Tutor - Tvoj virtualni prijatelj za učenje!")
st.markdown("Nema pitanja na koja AI ne zna odgovor! Postavi pitanje i učimo zajedno.")

# Inicijalizacija chat povijesti ako ne postoji
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Iteracija kroz sve poruke koje su pohranjene u povijesti razgovora (chat_history)
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Unos korisničkog pitanja
if user_input := st.chat_input("Postavi svoje pitanje..."):
    # Dodaj korisničku poruku u povijest
    user_msg = {"role": "user", "content": user_input}
    st.session_state.chat_history.append(user_msg)

    # Prikaži korisničko pitanje
    with st.chat_message("user"):
        st.write(user_input)

    # Pripremi payload s poviješću svih poruka
    payload = {"messages": st.session_state.chat_history}

    try:
        # Pošaljemo POST zahtjev na backend (FastAPI) s chat_history kako bi AI generirao odgovor
        response = requests.post("http://127.0.0.1:8000/chat/", json=payload)

        if response.status_code == 200:
            ai_response = response.json().get("response", "No response from AI")

            # Dodaj AI odgovor u chat_history
            assistant_msg = {"role": "assistant", "content": ai_response}
            st.session_state.chat_history.append(assistant_msg)

            # Prikaži AI odgovor
            with st.chat_message("assistant"):
                st.write(ai_response)

        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {str(e)}")

# Generiranje PDF-a s poviješću razgovora
if st.button("Spremi povijest razgovora kao PDF"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Dodaj Unicode font (preporučeni DejaVuSans)
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)  # Provjeri da je .ttf u istom folderu
    pdf.set_font('DejaVu', '', 14)

    # Dodaj naslov s emoji
    pdf.cell(200, 10, txt="📚 AI Tutor - Povijest razgovora", ln=True, align='C')

    # Dodaj svaku poruku iz povijesti razgovora
    pdf.ln(10)
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]

        # Formatiranje poruka
        if role == "user":
            pdf.set_font('DejaVu', '', 12)
            pdf.multi_cell(0, 10, f"User: {content}")  # multi_cell omogućava prelamanje linija
        else:
            pdf.set_font('DejaVu', '', 12)
            pdf.multi_cell(0, 10, f"Assistant: {content}")  # multi_cell omogućava prelamanje linija

        pdf.ln(5)  # Razmak između poruka

    # Pohrana PDF-a u lokalnu privremenu mapu
    pdf_output_path = "povijest_razgovora.pdf"
    pdf.output(pdf_output_path)

    # Omogućiti preuzimanje PDF-a
    with open(pdf_output_path, "rb") as f:
        st.download_button(
            label="Preuzmi PDF",
            data=f,
            file_name="povijest_razgovora.pdf",
            mime="application/pdf"
        )

    # Obavijesti korisnika da je PDF generiran
    st.success("PDF je uspješno generiran! Klikni na gumb za preuzimanje.")
