import sqlite3
import pickle
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu

from utils.database import calculate_bmi, calculate_calories, save_prediction, validate_numeric_input, save_test_result, get_doctors

st.set_page_config(page_title="Health Assistant - Patient Portal", layout="wide", page_icon="🧑‍⚕️")
import pickle
from collections import Counter

# Load the trained model
with open('D:/multiple-disease-prediction-streamlit-app-main/saved_models/diabetes_model.sav', 'rb') as model_file:
    diabetes_model = pickle.load(model_file)

if "patient_logged_in" not in st.session_state:
    st.session_state["patient_logged_in"] = False
    st.session_state["patient_id"] = False

if st.sidebar.button("Logout"):
    st.session_state["patient_id"] = None
    st.session_state["patient_logged_in"] = False
        
# Main application logic
if st.session_state["patient_id"]:
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=["Diabetes Prediction"],
            icons=["activity"],
            menu_icon="menu-down",
            default_index=0
        )

    if selected == "Diabetes Prediction":
        st.title("Diabetes Prediction")

        # Inputs for diabetes prediction
        col1, col2, col3 = st.columns(3)
        with col1:
            pregnancies = validate_numeric_input(st.text_input("Pregnancies"), "Pregnancies", min_val=0, max_val=20)
        with col2:
            glucose = validate_numeric_input(st.text_input("Glucose Level"), "Glucose Level", min_val=50, max_val=300)
        with col3:
            blood_pressure = validate_numeric_input(st.text_input("Blood Pressure"), "Blood Pressure", min_val=50, max_val=200)
        with col1:
            skin_thickness = validate_numeric_input(st.text_input("Skin Thickness"), "Skin Thickness", min_val=10, max_val=99)
        with col1:
            age = validate_numeric_input(st.text_input("Age"), "Age", min_val=1, max_val=99)
        with col2:
            insulin = validate_numeric_input(st.text_input("Insulin Level"), "Insulin Level", min_val=100, max_val=900)
        with col1:
            weight = validate_numeric_input(st.text_input("Weight (kg)"), "Weight", min_val=20, max_val=200)
        with col2:
            height = validate_numeric_input(st.text_input("Height (cm)"), "Height", min_val=50, max_val=250)
        with col2:
            diabetes_pedigree_function = validate_numeric_input(st.text_input("DiabetesPedigreeFunction") , "DiabetesPedigreeFunction" , min_val=0, max_val=1)

        gender = st.selectbox("Gender", ["Male", "Female"])
        activity_level = st.selectbox(
            "Activity Level",
            ["Sedentary", "Light", "Moderate", "Active", "Very Active"]
        )

        if "test_result" not in st.session_state:
            st.session_state["test_result"] = None

        if st.button("Predict Diabetes and Calculate Calories"):
            if None not in [pregnancies, glucose, blood_pressure, skin_thickness, insulin, weight, height , diabetes_pedigree_function , age]:
                bmi = calculate_bmi(weight, height)
                
                # Prepare input for the model
                input_features = np.array([[
                     pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi , diabetes_pedigree_function , age
                ]])
                # input_features = [
                #      pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age
                #                 ]
                
                # Make prediction
                prediction = diabetes_model.predict(input_features)[0]
                result = "Diabetic" if prediction == 1 else "Not Diabetic"
                calorie_result = calculate_calories(weight, height, int(pregnancies), gender, activity_level)

                # Save prediction
                input_data = {
                    "pregnancies": pregnancies,
                    "glucose": glucose,
                    "blood_pressure": blood_pressure,
                    "skin_thickness": skin_thickness,
                    "insulin": insulin,
                    "weight": weight,
                    "height": height,
                    "bmi": bmi,
                    "gender": gender,
                    "activity_level": activity_level
                }
                save_prediction(
                    st.session_state["patient_id"],
                    "diabetes",
                    str(input_data),
                    result
                )

                # Display results
                if result == "Diabetic":
                    st.markdown(f"<p style='font-weight:bold;'>Prediction: <span style='color:red;'>{result}</span></p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='font-weight:bold;'>Prediction: <span style='color:green;'>{result}</span></p>", unsafe_allow_html=True)
                st.info(f"Your BMI is: {bmi:.2f}")
                st.info(f"Your daily caloric need is: {calorie_result:.2f} calories.")
                if result == "Diabetic":
                    st.warning("You are diabetic. Please consult a doctor for detailed advice.")

                st.session_state["test_result"] = result  
                st.session_state["input_data"] = input_data

            else:
                st.error("Please correct the invalid inputs.")

        if st.session_state["test_result"]:
            st.subheader("Send Test Result to a Doctor")
            doctors = get_doctors()

            if doctors:
                if "selected_doctor" not in st.session_state:
                    st.session_state["selected_doctor"] = None

                doctor_options = {username: id for id, username in doctors}
                
                selected_doctor = st.selectbox(
                    "Select a Doctor",
                    options=list(doctor_options.keys()),
                    index=list(doctor_options.values()).index(st.session_state["selected_doctor"]) if st.session_state["selected_doctor"] else 0
                )
                st.session_state["selected_doctor"] = doctor_options[selected_doctor]

                if st.button("Send Result to Doctor"):
                    selected_doctor_id = st.session_state["selected_doctor"]

                    save_test_result(
                        st.session_state["patient_id"],
                        selected_doctor_id,
                        "Diabetes Prediction",
                        st.session_state["test_result"],
                        str(st.session_state["input_data"])
                    )

                    st.success(f"Test result sent to {selected_doctor.split(' (')[0]} successfully!")
            else:
                st.warning("No doctors available.")

if not st.session_state["patient_logged_in"]:
    st.switch_page("./pages/Login.py")