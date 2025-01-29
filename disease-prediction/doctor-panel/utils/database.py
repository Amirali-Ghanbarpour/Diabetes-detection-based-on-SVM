import sqlite3
import bcrypt

# ایجاد یا جایگزینی جدول doctors
def create_doctor_table():
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()

    # ایجاد جدول جدید با محدودیت‌های UNIQUE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT UNIQUE,
        medical_license TEXT UNIQUE
    )
    """)
    conn.commit()
    conn.close()


# به‌روزرسانی جدول predictions
def update_predictions_table():
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()

    # بررسی ستون‌های موجود
    cursor.execute("PRAGMA table_info(predictions);")
    columns = [column[1] for column in cursor.fetchall()]

    # اضافه کردن ستون username اگر وجود ندارد
    if "username" not in columns:
        cursor.execute("ALTER TABLE predictions ADD COLUMN username TEXT")
    
    conn.commit()
    conn.close()

# افزودن پزشک جدید
def add_doctor(username, password, email, medical_license):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("""
    INSERT INTO doctors (username, password, email, medical_license) 
    VALUES (?, ?, ?, ?)
    """, (username, hashed_password, email, medical_license))
    conn.commit()
    conn.close()

# احراز هویت پزشک
def authenticate_doctor(username, password):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM doctors WHERE username = ?", (username,))
    doctor = cursor.fetchone()
    conn.close()
    if doctor and bcrypt.checkpw(password.encode('utf-8'), doctor[1]):
        return doctor[0]  # Return doctor ID
    return None

import sqlite3

def get_doctor_username(doctor_id):
    try:
        conn = sqlite3.connect("health_assistant.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM doctors WHERE id = ?", (doctor_id,))
        doctor = cursor.fetchone()
        conn.close()

        if doctor:
            print(f"Doctor Name: {doctor[0]}")
            return doctor[0]
        else:
            print("Doctor not found.")
            return "Doctor not found."
    except Exception as e:
        print(f"Error: {e}")
        return "Error occurred."


def save_message(doctor_id, patient_id, message, sender_role):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (patient_id, doctor_id, message, sender_role)
        VALUES (?, ?, ?, ?)
    """, (patient_id, doctor_id, message, sender_role))
    conn.commit()
    conn.close()

def get_messages(doctor_id, patient_id):
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

def get_patients():
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM patients")
    patients = cursor.fetchall()
    conn.close()
    return patients

def get_latest_sent_test_results(doctor_id):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT patients.id, patients.username, predictions.result, MAX(predictions.created_at) AS latest_date
        FROM messages
        INNER JOIN predictions ON messages.patient_id = predictions.patient_id
        INNER JOIN patients ON patients.id = messages.patient_id
        WHERE messages.doctor_id = ?
            AND messages.sender_role = 'Patient'
            AND messages.message LIKE 'Test Type:%'
        GROUP BY patients.id
        ORDER BY latest_date DESC;
    """, (doctor_id,))
    results = cursor.fetchall()
    conn.close()
    return results



def get_test_results_from_messages(doctor_id):
    conn = sqlite3.connect("health_assistant.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT created_at, message
        FROM messages
        WHERE doctor_id = ? AND sender_role = 'Patient' AND message LIKE 'Test Type:%'
        ORDER BY created_at ASC
    """, (doctor_id,))
    results = cursor.fetchall()
    conn.close()
    # Parse the messages to extract test details
    data = []
    for created_at, message in results:
        try:
            inputs_start = message.find("Inputs:") + len("Inputs: ")
            inputs_data = json.loads(message[inputs_start:])
            inputs_data["Date"] = created_at
            data.append(inputs_data)
        except json.JSONDecodeError:
            print(f"Failed to parse message: {message}")
    
    return data

create_doctor_table()