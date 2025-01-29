import sqlite3
import bcrypt
import streamlit as st

from utils.database import add_doctor

# Set page configuration
# st.set_page_config(page_title="Health Assistant - Doctor Register", layout="wide", page_icon="🧑‍⚕️")

# مقداردهی اولیه وضعیت ورود پزشک
if "doctor_logged_in" not in st.session_state:
    st.session_state["doctor_logged_in"] = False

# صفحه رجیستر پزشکان
# def register_doctor_page():
st.title("Doctor Registration")
username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
medical_license = st.text_input("Medical License Number")

if st.button("Register"):
    if not medical_license.strip():
        st.error("Medical License Number is required.")
    else:
        try:
            add_doctor(username, password, email, medical_license)
            st.success("Doctor registered successfully. Please log in.")
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: doctors.username" in str(e):
                st.error("Username already exists.")
            elif "UNIQUE constraint failed: doctors.email" in str(e):
                st.error("Email already exists.")
            elif "UNIQUE constraint failed: doctors.medical_license" in str(e):
                st.error("Medical License Number already exists.")
            else:
                st.error("An error occurred during registration.")
