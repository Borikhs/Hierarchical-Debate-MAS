import pandas as pd

# Define patient information
patient_info = {
    "age": 77,
    "gender": "Male",
    "chief_complaint": "Severe shoulder pain and difficulty in shoulder movement, particularly exacerbated by arm elevation, along with multiple rib fractures and generalized muscle aches.",
    "vital_signs": {
        "temperature": 36.4,
        "respiratory_rate": 18,
        "heart_rate": 89,
        "blood_pressure": 107
    },
    "physical_examination": {
        "general": "Alert and oriented with mild diaphoresis due to pain.",
        "musculoskeletal": "Significant tenderness over the affected shoulder area with marked limitation of range of motion, suggestive of chronic musculoskeletal issues. Multiple tender points noted over the rib cage consistent with multiple rib fractures. Generalized myalgia noted throughout the musculature.",
        "neurological": "Mild discomfort reported in the upper extremity, indicative of possible radicular pain, likely involving multiple spinal levels."
    },
    "medical_history": {
        "past_medical_history": ["Parkinson’s Disease", "History of multiple minor falls increasing risk for fractures"]
    }
}

# Define top 4 likely diagnoses based on medical literature search results
top_diagnoses = [
    {"diagnosis": "Cervical palsy", "relevance_score": 62.6024},
    {"diagnosis": "Parkinson disease with neck and spine extensor weakness", "relevance_score": 61.6411},
    {"diagnosis": "Progressive supranuclear palsy", "relevance_score": 61.4406},
    {"diagnosis": "Postural instability due to Parkinson disease", "relevance_score": 61.2839}
]

# Define disposition levels
disposition_levels = {
    0: "Discharge",
    1: "Ward Admission",
    2: "ICU Admission"
}

# Predict top 4 most likely diagnoses for the patient
print("Top 4 Most Likely Diagnoses:")
for i, diagnosis in enumerate(top_diagnoses):
    print(f"{i+1}. {diagnosis['diagnosis']} (Relevance Score: {diagnosis['relevance_score']})")

# Predict disposition level based on patient's condition and medical history
predicted_disposition = 1  # Ward Admission
print(f"\nPredicted Disposition Level: {disposition_levels[predicted_disposition]}")