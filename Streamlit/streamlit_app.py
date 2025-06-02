import streamlit as st
from fpdf import FPDF
import requests
import re
import html
import os
import json
import random
import time
import matplotlib.pyplot as plt
import pandas as pd

users_json_path = "C:/Users/Korisnik/Desktop/AI_Tutor-3/Backend/users.json"
prijavljen = 0

# Funkcija za učitavanje pitanja iz JSON datoteke
def load_quiz_questions():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "..", "Backend", "initial_data.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        qa_entries = [item["fields"] for item in raw_data if item["model"] == "chatbot.qaentry"]
        return qa_entries
    except FileNotFoundError:
        st.error(f"❌ JSON datoteka nije pronađena na lokaciji: `{json_path}`")
        return []

def skrati_na_recenice(tekst):
    tekst = tekst.strip()
    if not tekst:
        return ""

    natuknice = re.split(r'[\n•\-–●]', tekst)
    natuknice = [n.strip() for n in natuknice if n.strip()]
    if len(natuknice) > 0:
        prva = natuknice[0]
        if len(prva) > 200:
            return prva[:200] + "..."
        elif len(natuknice) > 1:
            kombinirano = f"{prva}; {natuknice[1]}"
            return kombinirano if len(kombinirano) <= 220 else prva
        return prva

    recenice = re.split(r'(?<=[.!?])\s+', tekst)
    prva = recenice[0]
    if len(prva) >= 200 or len(recenice) == 1:
        return prva
    druga = recenice[1] if len(recenice) > 1 else ""
    kombinirano = f"{prva} {druga}".strip()
    return kombinirano if len(kombinirano) <= 220 else prva

# Ucitaj popis korisnika iz users.json
def load_users():
    try:
        with open(users_json_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Spremi korisnika u users.json
def save_users(users):
    with open(users_json_path, "w") as f:
        json.dump(users, f, indent=4)

# Dodaj pitanje u strukturu korisnika
def add_question_for_user(email, question):
    users = load_users()
    if email in users:
        if "questions" not in users[email]:
            users[email]["questions"] = []
        users[email]["questions"].append(question)
        save_users(users)

# Dodaj rezultat kviza u korisničke podatke
def add_quiz_attempt(email, course, score, max_score):
    users = load_users()
    if email not in users:
        users[email] = {"quiz_attempts": []}
    elif "quiz_attempts" not in users[email]:
        users[email]["quiz_attempts"] = []
    
    users[email]["quiz_attempts"].append({
        "course": course,
        "score": score,
        "max_score": max_score,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "attempt_number": len(users[email]["quiz_attempts"]) + 1
    })
    save_users(users)

# Prikaz grafova za kviz
def show_quiz_charts(email, course):
    users = load_users()
    if email not in users or "quiz_attempts" not in users[email]:
        return
    
    attempts = [a for a in users[email]["quiz_attempts"] if a["course"] == course]
    if not attempts:
        return
    
    df = pd.DataFrame(attempts)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(
        df['attempt_number'].astype(str),
        df['score'],
        color=['#4CAF50' if x == max(df['score']) else '#2196F3' for x in df['score']]
    )
    
    ax.set_title(f'Rezultati kviza za {course}')
    ax.set_xlabel('Broj pokušaja')
    ax.set_ylabel('Osvojeni bodovi')
    ax.set_ylim(0, df['max_score'].max() * 1.1)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom')
    
    st.pyplot(fig)

# Funkcija za generiranje opcija za kviz
def generate_options(correct_answer, all_answers):
    options = [correct_answer]
    distractors = random.sample([a for a in all_answers if a != correct_answer], k=3)
    options.extend(distractors)
    random.shuffle(options)
    return options

# Funkcija za formatiranje AI odgovora
def format_answer_parts(text: str) -> str:
    text = text.replace('', '-')
    text = html.escape(text)

    def indent_lists(t):
        return re.sub(r'\((i{1,3})\)', lambda m: f"\n&emsp;- ({m.group(1)})", t)

    parts = re.split(r'(?<!\w)([a-e]\))', text)
    formatted_parts = []
    current = ""

    for part in parts:
        if re.match(r'[a-e]\)', part):
            if current:
                formatted_parts.append(current.strip())
            current = f"<div style='margin-top:12px;'><b>{part}</b>"
        else:
            indented = indent_lists(part)
            indented = indented.replace('\n', '<br>')
            current += f"<div style='margin-left:1.5em;'>{indented}</div>"

    if current:
        formatted_parts.append(current.strip() + "</div><hr style='opacity:0.2;'/>")

    return "\n".join(formatted_parts)

# Inicijalizacija Streamlit aplikacije
st.set_page_config(page_title="AI Tutor", page_icon="🤖")
st.title("🎓 AI Tutor - Tvoj virtualni prijatelj za učenje!")
st.markdown("Nema pitanja na koja AI ne zna odgovor! Postavi pitanje i učimo zajedno.")

# ======== STANJA ========
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_questions" not in st.session_state:
    st.session_state.user_questions = []
if "start_quiz" not in st.session_state:
    st.session_state.start_quiz = False
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = []
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = None

# Rječnik kolegija
kolegiji = {
    "Programsko inženjerstvo": 1,
    "Ugradbeni računalni sustavi": 2,
    "Operacijski sustavi": 3,
}

# ======== DUGMIĆI ========
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔁 Reset"):
        st.session_state.chat_history = []
        st.session_state.user_questions = []
        st.session_state.quiz_data = []
        st.session_state.start_quiz = False
        st.session_state.quiz_results = []
        st.success("Chat je resetiran!")

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

    st.session_state.user_questions.append({"question": user_input})
    
    if st.session_state.get('logged_in', False):
        email = st.session_state['user_email']
        add_question_for_user(email, user_input)

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

# Sidebar opcije
sidebar_option = st.sidebar.radio(
    "Odaberi opciju:",
    ["Povijest pitanja", "Odabir kolegija", "Kviz znanja"]
)

# Sidebar opcije za povijest pitanja
if sidebar_option == "Povijest pitanja":
    history_option = st.sidebar.radio(
        "Prikaz pitanja:",
        ["Sva pitanja", "Nedavna pitanja"]
    )
    
    if history_option == "Sva pitanja":
        st.sidebar.markdown("### Povijest svih pitanja i odgovora")
        users = load_users()
        email = st.session_state['user_email']
        questions = users.get(email, {}).get("questions", [])
        if questions:
            for q in reversed(questions):
                st.sidebar.write(f"- {q}")
        else:
            st.sidebar.write("Još nema postavljenih pitanja.")
            
    elif history_option == "Nedavna pitanja":
        st.sidebar.markdown("### Nedavna pitanja i odgovori")
        users = load_users()
        email = st.session_state['user_email']
        questions = users.get(email, {}).get("questions", [])
        if questions: 
            for q in reversed(questions[-5:]):
                st.sidebar.write(f"- {q}")
        else:
            st.sidebar.write("Još nema postavljenih pitanja.")

elif sidebar_option == "Odabir kolegija":
    kolegij = st.sidebar.selectbox(
        "Odaberi kolegij:",
        ["Programsko inženjerstvo", "Ugradbeni računalni sustavi", "Operacijski sustavi"]
    )
elif sidebar_option == "Kviz znanja":
    st.markdown("## 🧠 Kviz znanja")
    selected_course = st.selectbox("Odaberi kolegij za kviz", list(kolegiji.keys()))

    if st.button("🎯 Pokreni kviz"):
        all_questions = load_quiz_questions()
        subject_id = kolegiji[selected_course]
        filtered = [q for q in all_questions if q.get("subject") == subject_id]

        if not filtered:
            st.warning("⚠️ Nema dostupnih pitanja za odabrani kolegij.")
        else:
            selected_questions = random.sample(filtered, min(12, len(filtered)))
            all_answers = [q["answer"] for q in all_questions]

            quiz_data = []
            for q in selected_questions:
                correct = skrati_na_recenice(q["answer"])
                other_answers = [skrati_na_recenice(a) for a in all_answers if a != q["answer"]]
                options = generate_options(correct, other_answers)

                quiz_data.append({
                    "pitanje": q["question"],
                    "opcije": options,
                    "tocan": q["answer"],
                    "predavanje": f"Predavanje {q['lecture_id']}"
                })

            st.session_state.quiz_data = quiz_data
            st.session_state.start_quiz = time.time()
            st.session_state.quiz_results = []
            st.session_state.selected_course = selected_course  # Spremamo odabrani kolegij
            st.rerun()

# Prikaz kviza ako je pokrenut
if st.session_state.start_quiz and st.session_state.quiz_data:
    st.title("📝 Kviz znanja")
    odgovori_korisnika = []

    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"### {i+1}. {q['pitanje']}")
        odgovor = st.radio("Odaberi odgovor:", q["opcije"], key=f"q_{i}")
        odgovori_korisnika.append((q, odgovor))

    if st.button("Završi kviz"):
        st.session_state.quiz_results = []
        for q, odgovor in odgovori_korisnika:
            tocno = odgovor == q["tocan"]
            vrijeme = round(time.time() - st.session_state.start_quiz, 2)
            bodovi = round((1.5 if tocno else 0) + max(0, 30 - vrijeme) / 30, 2)

            st.session_state.quiz_results.append({
                "pitanje": q["pitanje"],
                "odgovor": odgovor,
                "tocan": q["tocan"],
                "predavanje": q["predavanje"],
                "tocno": tocno,
                "vrijeme": vrijeme,
                "bodovi": bodovi
            })

        st.session_state.start_quiz = False
        st.rerun()

# Rezultati kviza
if st.session_state.quiz_results and not st.session_state.start_quiz:
    st.title("📊 Rezultati kviza")
    
    # Izračun bodova
    ukupno_bodova = sum(r["bodovi"] for r in st.session_state.quiz_results if r["tocno"])
    max_bodova = len(st.session_state.quiz_results) * 2.5
    
    # Prikaz pitanja i odgovora
    for i, r in enumerate(st.session_state.quiz_results):
        with st.expander(f"Pitanje {i+1}: {r['pitanje']}"):
            if r["tocno"]:
                st.success(f"✅ Točno ({round(r['bodovi'], 2)} bodova)")
            else:
                st.error("❌ Netočno")
            st.markdown(f"**Točan odgovor:** {r['tocan']}")
            st.markdown(f"**Predavanje:** {r['predavanje']}")
    
    st.markdown(f"## 🏆 Ukupno bodova: **{round(ukupno_bodova, 2)}** / {max_bodova}")

    # PRIKAZ GRAFA - OBAVEZNO ZA SVE
    course = st.session_state.get('selected_course', 'Nepoznat kolegij')
    
    # Generiraj jedinstveni ID za sesiju
    session_id = st.session_state.get('session_id', str(random.randint(1000, 9999)))
    st.session_state.session_id = session_id
    
    # Spremi rezultat
    quiz_data = {
        "session_id": session_id,
        "course": course,
        "score": ukupno_bodova,
        "max_score": max_bodova,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if 'quiz_history' not in st.session_state:
        st.session_state.quiz_history = []
    
    st.session_state.quiz_history.append(quiz_data)
    
    # Priprema podataka za graf
    attempts = [q for q in st.session_state.quiz_history if q["course"] == course]
    
    if attempts:
        st.markdown("### 📈 Povijest pokušaja")
        
        # Kreiranje grafa
        fig, ax = plt.subplots(figsize=(10, 4))
        
        attempt_nums = [f"Pokušaj {i+1}" for i in range(len(attempts))]
        scores = [a["score"] for a in attempts]
        
        colors = ['#4CAF50' if score == max(scores) else '#2196F3' for score in scores]
        bars = ax.bar(attempt_nums, scores, color=colors)
        
        # Postavke grafa
        ax.set_title(f'Rezultati za {course}')
        ax.set_xlabel('Pokušaj')
        ax.set_ylabel('Bodovi')
        ax.set_ylim(0, max(scores)*1.2)
        
        # Dodavanje vrijednosti na stupce
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height, 
                    f'{height:.1f}', ha='center', va='bottom')
        
        st.pyplot(fig)
    else:
        st.info("Ovo je vaš prvi pokušaj kviza")

    if st.button("🧹 Zatvori rezultate"):
        st.session_state.quiz_results = []
        st.session_state.quiz_data = []
        st.rerun()

# Generiranje PDF-a s poviješću razgovora
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

        if role == "user":
            pdf.set_font('DejaVu', '', 12)
            pdf.multi_cell(0, 10, f"User: {content}")
        else:
            pdf.set_font('DejaVu', '', 12)
            pdf.multi_cell(0, 10, f"Assistant: {content}")
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

# Prijava/odjava u sidebaru
if st.session_state.get('logged_in', False):
    st.sidebar.success(f"Prijavljeni ste kao: {st.session_state['user_name']} ({st.session_state['user_email']})")
    if st.sidebar.button("❌ Odjavi se", key="logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = None
        st.session_state['user_name'] = None
        st.session_state.chat_history = []
else:
    if st.sidebar.button("🔑 Prijavi se"):
        st.switch_page("pages/login.py")