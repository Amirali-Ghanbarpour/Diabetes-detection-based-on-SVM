import sqlite3
import bcrypt
import streamlit as st
from streamlit_option_menu import option_menu
from utils.database import authenticate_patient
# Sidebar for authentication
if "patient_id" not in st.session_state:
    st.session_state["patient_id"] = None


st.title("Patient Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
if st.button("Login"):
    patient_id = authenticate_patient(username, password)
    if patient_id:
        st.session_state["patient_logged_in"] = True
        st.session_state["patient_id"] = patient_id
        st.success("Login successful.")
        st.switch_page("./Dashboard.py")
    else:
        st.error("Invalid username or password.")
