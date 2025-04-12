import streamlit as st
from fpdf import FPDF
import requests

# Inicijalizacija Streamlit aplikacije
st.set_page_config(page_title="AI Tutor", page_icon="🤖")
st.title("🎓 AI Tutor - Tvoj virtualni prijatelj za učenje!")
st.markdown("Nema pitanja na koja AI ne zna odgovor! Postavi pitanje i učimo zajedno.")

# Inicijalizacija chat povijesti
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_questions" not in st.session_state:
    st.session_state.user_questions = []

# ======== DUGMIĆI ========
col1, col2, col3, col4 = st.columns(4)

#izrada reset buttona
with col1:
    if st.button("🔁 Reset"):
        st.session_state.chat_history = []
        st.success("Chat je resetiran!")

# Sidebar opcije
sidebar_option = st.sidebar.radio(
    "Odaberi opciju:",
    ["Povijest pitanja", "Odabier kolegija", "Kviz znanja"]
)

# Dinamički sadržaj na temelju odabrane opcije u sidebaru
if sidebar_option == "Povijest pitanja":
    # Odabir prikaza svih pitanja ili nedavnih
    history_option = st.sidebar.radio(
        "Prikaz pitanja:",
        ["Sva pitanja", "Nedavna pitanja"]
    )

    #ako je odabrana opcija Povijest pitanja postavlja se opcija za prikaz svih ili nedavnih pitanja
    if history_option == "Sva pitanja":
        st.sidebar.markdown("### Povijest svih pitanja")
        if st.session_state.user_questions:
            for i, question in enumerate(st.session_state.user_questions, 1):
                st.sidebar.markdown(f"**{i}.** {question}")
        else:
            st.sidebar.write("Još nema postavljenih pitanja.")
    
    elif history_option == "Nedavna pitanja":
        st.sidebar.markdown("### Nedavna pitanja")
        # Prikaz najnovijih 5 pitanja, ili manje ako ima manje pitanja
        recent_questions = st.session_state.user_questions[-5:]
        if recent_questions:
            for i, question in enumerate(reversed(recent_questions), 1):
                st.sidebar.markdown(f"**{len(recent_questions) - i + 1}.** {question}")
        else:
            st.sidebar.write("Još nema postavljenih pitanja.")

#odabir kolegija koji ima padajući izbornik s kolegijima
elif sidebar_option == "Odabier kolegija":
    kolegij = st.sidebar.selectbox(
    "Odaberi kolegij:",
    ["Programsko inženjerstvo", "Baze podataka", "Računalne mreže", "Umjetna inteligencija"]
)
else:
    st.sidebar.markdown("Kviz znanja")
    st.sidebar.write("Kviz znanja koji ispituje znanje o odabranom kolegiju.")
    st.sidebar.button("Pokreni kviz")


# Unos korisničkog pitanja
if user_input := st.chat_input("Postavi svoje pitanje..."):
    st.session_state.chat_history.append({"role": "user", "content": user_input})

     # Spremi pitanje u zasebnu listu
    st.session_state.user_questions.append(user_input)

# Ako je dodana nova poruka korisnika
if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
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
