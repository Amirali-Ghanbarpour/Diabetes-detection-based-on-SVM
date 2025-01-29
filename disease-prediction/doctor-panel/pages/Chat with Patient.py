import sqlite3
import bcrypt
import streamlit as st
import pandas as pd
from utils.database import get_messages, save_message, get_patients

# تنظیمات صفحه
st.set_page_config(page_title="Health Assistant - Chat with Patient", layout="wide", page_icon="🧑‍⚕️")

# بررسی وضعیت ورود پزشک
if "doctor_logged_in" not in st.session_state:
    st.session_state["doctor_logged_in"] = False
    st.session_state["doctor_id"] = None

if st.sidebar.button("Logout"):
    st.session_state["doctor_id"] = None
    st.session_state["doctor_logged_in"] = False

if not st.session_state["doctor_logged_in"]:
    st.switch_page("./pages/Login.py")

if "message_sent" not in st.session_state:
    st.session_state["message_sent"] = False

# دریافت لیست بیماران
patients = get_patients()

if not patients:
    st.warning("No Patient.")
else:
    patient_options = {username: id for id, username in patients}
    
    default_patient = None
    if "selected_patient" in st.session_state:
        default_patient = next(
            (key for key, value in patient_options.items() if value == st.session_state["selected_patient"]),
            None
        )

    selected_patient = st.selectbox(
        "Select a Patient", options=list(patient_options.keys()), index=list(patient_options.keys()).index(default_patient) if default_patient else 0
    )

    # دریافت آیدی بیمار انتخاب شده
    patient_id = patient_options[selected_patient]

    # نمایش تاریخچه چت
    chat_history = get_messages(st.session_state["doctor_id"], int(patient_id))

    # ارسال پیام جدید
    new_message = st.text_area("Write your message")
    if st.button("Send"):
        if new_message:
            save_message(st.session_state["doctor_id"], int(patient_id), new_message, 'Doctor')
            chat_history = get_messages(st.session_state["doctor_id"], int(patient_id))
            st.session_state["message_sent"] = True
            st.success("Message sent successfully!")
        else:
            st.error("Please write a message before sending.")

    # نمایش پیام‌ها
    if chat_history:
        # معکوس کردن ترتیب پیام‌ها برای نمایش آخرین پیام در بالا
        chat_history = chat_history[::-1]

        for message, timestamp, sender in chat_history:
            # نمایش نتایج آزمایش‌ها
            if "Test Type" in message and "Result" in message:
                message_lines = message.split("\n")
                test_type = message_lines[0]
                result = message_lines[1]
                inputs = eval(message_lines[2].split(": ", 1)[1])  # تبدیل رشته Inputs به دیکشنری

                # استفاده از expander برای نمایش اطلاعات
                with st.expander(f"🔬  {test_type} | Result {result.split(': ')[1]}", expanded=False):
                    # نمایش اطلاعات به صورت مرتب
                    st.markdown(
                        f"""
                        <div style='padding: 15px; background-color: #f5f7fa; border-radius: 10px; margin-bottom: 10px;'>
                            <p style="font-size: 16px; font-weight: bold; color: #34495e;">{test_type}</p>
                            <p style="font-size: 16px; font-weight: bold; color: #e74c3c;">Result: {result.split(': ')[1]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # تبدیل داده‌ها به DataFrame برای نمایش بهتر
                    inputs_df = pd.DataFrame(inputs.items(), columns=["Parameters", "Values"])

                    # نمایش جدول نتایج
                    st.markdown(
                        f"""
                        <div style='background-color: #ffffff; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);'>
                            <h4 style='color: #34495e; font-family: Arial, sans-serif;'>Result Table</h4>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.table(inputs_df)
            else:
                # نمایش پیام‌های معمولی
                if sender == "Doctor":
                    st.markdown(f"""
                    <div style='text-align: left; background-color: #e3f2fd; border-radius: 10px; padding: 10px; margin: 5px;'>
                        <strong>You:</strong><br>{message}<br><small>{timestamp}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='text-align: right; background-color: #e8f5e9; border-radius: 10px; padding: 10px; margin: 5px;'>
                        <strong>Patient:</strong><br>{message}<br><small>{timestamp}</small>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No messages found.")
