import streamlit as st
from fpdf import FPDF
import requests
import re
import html

# Inicijalizacija Streamlit aplikacije
st.set_page_config(page_title="AI Tutor", page_icon="🤖")
st.title("🎓 AI Tutor - Tvoj virtualni prijatelj za učenje!")
st.markdown("Nema pitanja na koja AI ne zna odgovor! Postavi pitanje i učimo zajedno.")

# Funkcija za formatiranje AI odgovora
def format_answer_parts(text: str) -> str:
    # Zamjena specijalnih bullet znakova
    text = text.replace('', '-')

    # Escape HTML znakova
    text = html.escape(text)

    # Funkcija za uvlačenje podsekcija (i), (ii), (iii)
    def indent_lists(t):
        return re.sub(r'\((i{1,3})\)', lambda m: f"\n&emsp;- ({m.group(1)})", t)

    # Razdvajanje na glavne sekcije a), b), c)... (dinamički samo za a-e)
    parts = re.split(r'(?<!\w)([a-e]\))', text)
    formatted_parts = []
    current = ""

    for part in parts:
        if re.match(r'[a-e]\)', part):
            if current:
                formatted_parts.append(current.strip())
            current = f"<div style='margin-top:12px;'><b>{part}</b>"
        else:
            # Uvlačenje podsekcija i dodavanje teksta
            indented = indent_lists(part)
            # Zamjena novih redova sa <br> radi HTML prikaza
            indented = indented.replace('\n', '<br>')
            current += f"<div style='margin-left:1.5em;'>{indented}</div>"

    if current:
        formatted_parts.append(current.strip() + "</div><hr style='opacity:0.2;'/>")

    return "\n".join(formatted_parts)

# ======== DUGMIĆI ========
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔁 Reset"):
        st.session_state.chat_history = []
        st.session_state.user_questions = []
        st.success("Chat je resetiran!")

# Inicijalizacija chat povijesti
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_questions" not in st.session_state:
    st.session_state.user_questions = []

# Sidebar opcije
sidebar_option = st.sidebar.radio(
    "Odaberi opciju:",
    ["Povijest pitanja", "Odabier kolegija", "Kviz znanja"]
)

if sidebar_option == "Povijest pitanja":
    history_option = st.sidebar.radio(
        "Prikaz pitanja:",
        ["Sva pitanja", "Nedavna pitanja"]
    )
    if history_option == "Sva pitanja":
        st.sidebar.markdown("### Povijest svih pitanja i odgovora")
        if st.session_state.user_questions:
            for i, item in enumerate(reversed(st.session_state.user_questions), 1):
                st.sidebar.markdown(f"**{i}. Pitanje:** {item['question']}")
        else:
            st.sidebar.write("Još nema postavljenih pitanja.")
    elif history_option == "Nedavna pitanja":
        st.sidebar.markdown("### Nedavna pitanja i odgovori")
        recent_qna = st.session_state.user_questions[-5:][::-1]
        if recent_qna:
            for i, item in enumerate(recent_qna, 1):
                st.sidebar.markdown(f"**{i}.** {item['question']}")
        else:
            st.sidebar.write("Još nema nedavnih pitanja.")

elif sidebar_option == "Odabier kolegija":
    kolegij = st.sidebar.selectbox(
        "Odaberi kolegij:",
        ["Programsko inženjerstvo", "Baze podataka", "Računalne mreže", "Umjetna inteligencija"]
    )
else:
    st.sidebar.markdown("Kviz znanja")
    st.sidebar.write("Kviz znanja koji ispituje znanje o odabranom kolegiju.")
    st.sidebar.button("Pokreni kviz")

# Prikazivanje poruka u povijesti razgovora
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(format_answer_parts(message["content"]), unsafe_allow_html=True)
        else:
            st.write(message["content"])

# Unos korisničkog pitanja
if user_input := st.chat_input("Postavi svoje pitanje..."):
    user_msg = {"role": "user", "content": user_input}
    st.session_state.chat_history.append(user_msg)
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.user_questions.append({
        "question": user_input
    })

# Obrada i prikaz AI odgovora
if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
    payload = {"messages": st.session_state.chat_history}

    try:
        response = requests.post("http://127.0.0.1:8000/chat/", json=payload)

        if response.status_code == 200:
            ai_response = response.json().get("response", "No response from AI")
            assistant_msg = {"role": "assistant", "content": ai_response}
            st.session_state.chat_history.append(assistant_msg)

            with st.chat_message("assistant"):
                st.markdown(format_answer_parts(ai_response), unsafe_allow_html=True)
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {str(e)}")

# Generiranje PDF-a
if st.button("Spremi povijest razgovora kao PDF"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)

    pdf.cell(200, 10, txt="📚 AI Tutor - Povijest razgovora", ln=True, align='C')
    pdf.ln(10)

    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        formatted_content = format_answer_parts(content) if role == "assistant" else content

        pdf.set_font('DejaVu', '', 12)
        prefix = "Assistant:" if role == "assistant" else "User:"
        pdf.multi_cell(0, 10, f"{prefix} {formatted_content}")
        pdf.ln(5)

    pdf_output_path = "povijest_razgovora.pdf"
    pdf.output(pdf_output_path)

    with open(pdf_output_path, "rb") as f:
        st.download_button(
            label="Preuzmi PDF",
            data=f,
            file_name="povijest_razgovora.pdf",
            mime="application/pdf"
        )

    st.success("PDF je uspješno generiran! Klikni na gumb za preuzimanje.")


#Login i register

@st.dialog("Register")
def register():
    #Register pop-up
        st.subheader("Register")
        username = st.text_input("Username", key="register_username")
        password = st.text_input("Password", type="password", key="register_password")
        # Slanje podataka u bazu
        if st.button("Register", key="register_submit"):
            response = requests.post(f"http://127.0.0.1:8000/register/", json={
                "username": username,
                "password": password
            })
            data = response.json()
            if data["status"] == "success":
                st.success(data.get("message", "Registered!"))
            else:
                st.error(data.get("message", "Registration failed"))

@st.dialog("Login")
def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_submit"):
        try:
            # Pokušaj prijave
            response = requests.post("http://127.0.0.1:8000/login/", json={
                "username": username,
                "password": password
            })
            
            data = response.json()

            # Provjeri status prijave
            if data.get("status") == "success":
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Logged in!")
                st.rerun()
            else:
                st.error(data.get("message", "Login failed."))

        except requests.exceptions.RequestException:
            st.error("Could not connect to the login server.")
        except ValueError:
            st.error("Invalid response from the server.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")


# Prikaz na ekranu dok je korisnik prijavljen
def main_app():
    st.subheader(f"Welcome {st.session_state['username']}")
    # Gumb za logout
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()


def main():
    # Pokazivanje prijave i registracije dok nismo prijavljeni ili pokazivanje pogleda prijavljenog korisnika
    if not st.session_state.get("logged_in"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                login()
        with col2:
            if st.button("Register"):
                register()
    else:
        main_app()

# Pokretanje aplikacije
if __name__ == "__main__":
    main()