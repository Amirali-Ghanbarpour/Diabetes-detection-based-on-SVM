import sqlite3
import bcrypt
import streamlit as st
from utils.database import add_patient

# Sidebar for authentication
if "patient_id" not in st.session_state:
    st.session_state["patient_id"] = None


st.title("Register")
username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Register"):
    try:
        add_patient(username, password, email)
        st.success("Registered successfully. Please log in.")
    except sqlite3.IntegrityError:
        st.error("Username already exists.")