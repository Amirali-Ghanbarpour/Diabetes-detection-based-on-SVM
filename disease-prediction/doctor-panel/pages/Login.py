import sqlite3
import bcrypt
import streamlit as st

from utils.database import authenticate_doctor
# from Doctor import doctor_portal_page

# Set page configuration
st.set_page_config(page_title="Health Assistant - Doctor Login", layout="wide", page_icon="🧑‍⚕️")

# صفحه ورود پزشکان
# def login_doctor_page():
st.title("Doctor Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
if st.button("Login"):
    doctor_id = authenticate_doctor(username, password)
    if doctor_id:
        st.session_state["doctor_logged_in"] = True
        st.session_state["doctor_id"] = doctor_id
        st.success("Login successful.")
        st.switch_page("./Dashboard.py")

    else:
        st.error("Invalid username or password.")




