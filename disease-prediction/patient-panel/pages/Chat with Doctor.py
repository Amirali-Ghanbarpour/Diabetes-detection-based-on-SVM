import sqlite3
import bcrypt
import streamlit as st
import pandas as pd
from utils.database import get_messages, save_message, get_doctors

# Set page configuration
st.set_page_config(page_title="Health Assistant - Chat with your own Doctor", layout="wide", page_icon="\U0001f9d1‍⚕️")

if "patient_logged_in" not in st.session_state:
    st.session_state["patient_logged_in"] = False
    st.session_state["patient_id"] = False

if st.sidebar.button("Logout"):
    st.session_state["patient_id"] = None
    st.session_state["patient_logged_in"] = False

if not st.session_state["patient_logged_in"]:
    st.switch_page("./pages/Login.py")

if "message_sent" not in st.session_state:
    st.session_state["message_sent"] = False

doctors = get_doctors()

if not doctors:
    st.warning("No Doctors.")
else:

    doctor_options = {username: id for id, username in doctors}
    selected_doctor = st.selectbox("Select a Doctor", options=list(doctor_options.keys()))

    # دریافت آیدی بیمار انتخاب شده
    doctor_id = doctor_options[selected_doctor]

    # نمایش چت
    chat_history = get_messages(st.session_state["patient_id"], int(doctor_id))

    # ارسال پیام جدید
    new_message = st.text_area("Write your message")
    if st.button("Send"):
        if new_message:
            save_message(st.session_state["patient_id"], int(doctor_id), new_message, 'Patient')
            chat_history = get_messages(st.session_state["patient_id"], int(doctor_id))
            st.session_state["message_sent"] = True
            st.success("Message sent successfully!")
        else:
            st.error("Please write a message before sending.")

    if chat_history:
        # معکوس کردن ترتیب پیام‌ها برای نمایش آخرین پیام در بالا
        chat_history = chat_history[::-1]

        for message, timestamp, sender in chat_history:
            if "Test Type" in message and "Result" in message:

                # جدا کردن بخش Inputs از پیام
                message_lines = message.split("\n")
                test_type = message_lines[0]
                result = message_lines[1]
                inputs = eval(message_lines[2].split(": ", 1)[1])  # تبدیل رشته Inputs به دیکشنری

                # استفاده از expander برای نمایش اطلاعات
                with st.expander(f"\U0001f52c  {test_type} | Result {result.split(': ')[1]}", expanded=False):
                    # تبدیل داده‌ها به DataFrame برای نمایش بهتر
                    inputs_df = pd.DataFrame(inputs.items(), columns=["Parameters", "Value"])

                    # نمایش اطلاعات به صورت جدول
                    st.markdown(
                        f"""
                        <div style='padding: 15px; background-color: #f5f7fa; border-radius: 10px; margin-bottom: 10px;'>
                            <p style="font-size: 16px; font-weight: bold; color: #34495e;">{test_type}</p>
                            <p style="font-size: 16px; font-weight: bold; color: #e74c3c;">Result: {result.split(': ')[1]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.table(inputs_df)
            else:
                # نمایش پیام‌های معمولی
                if sender == "Patient":
                    st.markdown(f"""
                    <div style='text-align: right; background-color: #e8f5e9; border-radius: 10px; padding: 10px; margin: 5px;'>
                        <strong>You:</strong><br>{message}<br><small>{timestamp}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='text-align: left; background-color: #e3f2fd; border-radius: 10px; padding: 10px; margin: 5px;'>
                        <strong>Doctor:</strong><br>{message}<br><small>{timestamp}</small>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No messages found.")
