import pandas as pd

# Define patient information
patient_info = {
    "Age": 77,
    "Gender": "Male",
    "Chief Complaint": "Severe shoulder pain, difficulty in shoulder movement, multiple rib fractures, generalized muscle aches",
    "Medical History": ["Parkinson's Disease", "History of multiple minor falls"],
    "Vital Signs": {
        "Temperature": 36.4,
        "Respiratory Rate": 18,
        "Heart Rate": 89,
        "Blood Pressure": 107
    }
}

# Define top 4 most likely diagnoses based on medical literature search results
top_diagnoses = [
    {"Diagnosis": "Parkinson's Disease", "Relevance Score": 63.5753},
    {"Diagnosis": "Isolated Neck Extensor Myopathy", "Relevance Score": 62.6403},
    {"Diagnosis": "Bent Spine Syndrome (Camptocormia)", "Relevance Score": 62.5815},
    {"Diagnosis": "Multiple Rib Fractures with Musculoskeletal Pain", "Relevance Score": 62.3762}
]

# Define disposition levels
disposition_levels = {
    0: "Discharge",
    1: "Observation / short-term monitoring",
    2: "Admission"
}

# Predict top 4 most likely diagnoses and disposition level based on patient information and medical literature search results
predicted_diagnoses = [diagnosis["Diagnosis"] for diagnosis in top_diagnoses]
predicted_disposition_level = 1  # Observation / short-term monitoring, considering the patient's age, medical history, and severity of symptoms

print("Predicted Top 4 Most Likely Diagnoses:")
for i, diagnosis in enumerate(predicted_diagnoses):
    print(f"{i+1}. {diagnosis}")

print(f"\nPredicted Disposition Level: {disposition_levels[predicted_disposition_level]}")