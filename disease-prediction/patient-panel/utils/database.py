import sqlite3
import bcrypt
import streamlit as st

# Database setup
def create_database():
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    # Create patients table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT
    )
    """)
    # Create predictions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        prediction_type TEXT,
        input_data TEXT,
        result TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        message TEXT,
        sender_role TEXT DEFAULT 'Patient',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)
    
    conn.commit()
    conn.close()

def add_patient(username, password, email):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO patients (username, password, email) VALUES (?, ?, ?)",
                   (username, hashed_password, email))
    conn.commit()
    conn.close()

def authenticate_patient(username, password):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM patients WHERE username = ?", (username,))
    patient = cursor.fetchone()
    conn.close()
    if patient and bcrypt.checkpw(password.encode('utf-8'), patient[1]):
        return patient[0] 
    return None

def save_prediction(patient_id, prediction_type, input_data, result):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO predictions (patient_id, prediction_type, input_data, result) VALUES (?, ?, ?, ?)",
                   (patient_id, prediction_type, input_data, result))
    conn.commit()
    conn.close()

def calculate_calories(weight, height, age, gender, activity_level):
    """
    Calculate daily caloric needs based on user's details.
    """
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_multiplier = {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Active": 1.725,
        "Very Active": 1.9
    }
    return bmr * activity_multiplier[activity_level]

def calculate_bmi(weight, height):
    """
    Calculate BMI based on weight (kg) and height (cm).
    """
    if height > 0:
        return weight / ((height / 100) ** 2)
    return None

def validate_numeric_input(value, field_name, min_val=None, max_val=None):
     """
     Validate that the input is a numeric value and within a specified range.
     """
     try:
         value = float(value)
         if min_val is not None and value < min_val:
             st.error(f"{field_name} must be at least {min_val}.")
             return None
         if max_val is not None and value > max_val:
             st.error(f"{field_name} must be at most {max_val}.")
             return None
         return value
     except ValueError:
         #st.error(f"Invalid input in {field_name}. Please enter a numeric value.")
         return None

def save_message(patient_id, doctor_id, message, sender_role):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (patient_id, doctor_id, message, sender_role)
        VALUES (?, ?, ?, ?)
    """, (patient_id, doctor_id, message, sender_role))
    conn.commit()
    conn.close()

def get_messages(patient_id, doctor_id):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT message, created_at, sender_role
        FROM messages
        WHERE (patient_id = ? AND doctor_id = ?)
           OR (doctor_id = ? AND patient_id = ?)
        ORDER BY created_at ASC
    """, (patient_id, doctor_id, doctor_id, patient_id))
    messages = cursor.fetchall()
    conn.close()
    return messages

def get_doctors():
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM doctors")
    doctors = cursor.fetchall()
    conn.close()
    return doctors
    
# def save_test_result(patient_id, doctor_id, test_type, test_result):
#     conn = sqlite3.connect("health_assistant.db")
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO messages (patient_id, doctor_id, message, sender_role)
#         VALUES (?, ?, ?, ?)
#     """, (patient_id, doctor_id, f"Test Type: {test_type}\nResult: {test_result}", 'Patient'))
#     conn.commit()
#     conn.close()

def save_test_result(patient_id, doctor_id, test_type, test_result, input_data):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    message_content = f"Test Type: {test_type}\nResult: {test_result}\nInputs: {input_data}"
    cursor.execute("""
        INSERT INTO messages (patient_id, doctor_id, message, sender_role)
        VALUES (?, ?, ?, ?)
    """, (patient_id, doctor_id, message_content, 'Patient'))
    conn.commit()
    conn.close()




# Initialize the database
create_database()

    