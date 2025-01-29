import sqlite3
import bcrypt
import streamlit as st

from utils.database import get_doctor_username, get_latest_sent_test_results

# Set page configuration
st.set_page_config(page_title="Health Assistant - Doctor Portal", layout="wide", page_icon="🧑‍⚕️")

# Add custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        font-family: 'Arial', sans-serif;
        background-color: #f5f5f5;
        padding: 20px;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2c3e50;
        color: white;
    }
    .st-info {
        font-size: 18px;
        color: #34495e;
        background-color: #ecf0f1;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .st-title {
        font-size: 26px;
        color: #2c3e50;
        font-weight: bold;
        margin-bottom: 25px;
        text-align: center;
    }
    .st-subheader {
        font-size: 20px;
        color: #16a085;
        margin-bottom: 15px;
    }
    .patient-section {
        background-color: #ecf0f1;
        border-left: 4px solid #3498db;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# مقداردهی اولیه وضعیت ورود پزشک
if "doctor_logged_in" not in st.session_state:
    st.session_state["doctor_logged_in"] = False
    st.session_state["doctor_id"] = False

# صفحه پزشک
st.sidebar.success("Doctor logged in successfully!")
st.markdown("<div class='st-title'>Doctor Portal</div>", unsafe_allow_html=True)
docter_username = get_doctor_username(st.session_state["doctor_id"])

# دکمه Logout
if st.sidebar.button("Logout"):
    st.session_state["doctor_logged_in"] = False

if not st.session_state["doctor_logged_in"]:
    st.switch_page("./pages/Login.py")

latest_results = get_latest_sent_test_results(st.session_state["doctor_id"])

if latest_results:
    st.markdown("<div class='st-subheader'>Latest Test Results Sent by Patients</div>", unsafe_allow_html=True)

    # تفکیک دیابتیک و غیر دیابتیک
    diabetics = [result for result in latest_results if result[2] == "Diabetic"]
    non_diabetics = [result for result in latest_results if result[2] == "Not Diabetic"]

    # نمایش دیابتیک‌ها
    st.markdown("<div class='st-subheader'>Diabetic Patients</div>", unsafe_allow_html=True)
    if diabetics:
        for patient_id, username, result, created_at in diabetics:
            unique_key = f"diabetic-{patient_id}"  # کلید منحصربه‌فرد بر اساس بیمار
            st.markdown(f"<div class='patient-section'><span>Chat with <strong>{username}</strong> - {result} (Sent at {created_at})</span>", unsafe_allow_html=True)
            if st.button(f"Chat with {username}", key=unique_key):
                st.session_state["selected_patient"] = patient_id
                st.session_state["selected_username"] = username
                st.switch_page("./pages/Chat with Patient.py")
    else:
        st.info("No diabetic test results.")

    # نمایش غیر دیابتیک‌ها
    st.markdown("<div class='st-subheader'>Non-Diabetic Patients</div>", unsafe_allow_html=True)
    if non_diabetics:
        for patient_id, username, result, created_at in non_diabetics:
            unique_key = f"non-diabetic-{patient_id}"  # کلید منحصربه‌فرد بر اساس بیمار
            st.markdown(f"<div class='patient-section'><span>Chat with <strong>{username}</strong> - {result} (Sent at {created_at})</span>", unsafe_allow_html=True)
            if st.button(f"Chat with {username}", key=unique_key):
                st.session_state["selected_patient"] = patient_id
                st.session_state["selected_username"] = username
                st.switch_page("./pages/Chat with Patient.py")
    else:
        st.info("No non-diabetic test results.")
else:
    st.info("No test results available.")
