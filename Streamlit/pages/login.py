import streamlit as st
import json
import hashlib

users_json_path = "../Backend/users.json"

hide_sidebar_style = """
<style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
</style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

def load_users():
    try:
        with open(users_json_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open(users_json_path, "w") as f:
        json.dump(users, f, indent=4)

def generate_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(stored_hash, password):
    return stored_hash == hashlib.sha256(password.encode()).hexdigest()


st.set_page_config(page_title="Prijava", page_icon="🤖")
st.title("Prijava/Registracija")

# Inicijalizacija session_state za formu
if 'show_form' not in st.session_state:
    st.session_state.show_form = True

# Radio za tip korisnika
user_type = st.radio("Jeste li novi korisnik?", ["Postojeći", "Novi korisnik"], horizontal=True)

# Forma
with st.form("auth_form"):
    if user_type == "Novi korisnik":
        name = st.text_input("Ime i prezime")
        email = st.text_input("Email")
        password = st.text_input("Lozinka", type="password")
    else:
        email = st.text_input("Email")
        password = st.text_input("Lozinka", type="password")

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        submit = st.form_submit_button("Prijavi se")
    with col3:
        cancel = st.form_submit_button("Odustani")

    if submit:
        users = load_users()
        try:
            if user_type == "Novi korisnik":
                if email in users:
                    st.error("🔴 Email već postoji!")
                else:
                    # Hashiranje lozinke
                    hashed_password = generate_password_hash(password)
                    users[email] = {
                        "name": name,
                        "password": hashed_password
                    }
                    save_users(users)
                    st.session_state.update({
                        'logged_in': True,
                        'user_email': email,
                        'user_name': name
                    })
                    st.switch_page("streamlit_app.py")
            else:
                user_data = users.get(email)
                if user_data and check_password_hash(user_data["password"], password):
                    st.session_state.update({
                        'logged_in': True,
                        'user_email': email,
                        'user_name': user_data["name"]
                    })
                    st.switch_page("streamlit_app.py")
                else:
                    st.error("🔴 Pogrešan email ili lozinka!")
        except Exception as e:
            st.error(f"Greška: {str(e)}")

    if cancel:
        st.session_state.show_form = False
        st.switch_page("streamlit_app.py")
