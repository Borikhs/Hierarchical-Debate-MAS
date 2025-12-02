import pandas as pd
import numpy as np

def predict_diagnoses_and_disposition(patient_info):
    diagnoses_df = pd.DataFrame({
        'primary_dx_code': ['M7918', 'S2244', 'M754', 'M5410', 'G20'],
        'primary_dx_name': [
            'Multiple rib fractures',
            'Shoulder region injury',
            'Generalized myalgia',
            'Radicular pain',
            'Parkinson’s Disease'
        ],
        'num_secondary_dx': [1, 2, 2, 1, 3]
    })

    similar_patients = pd.DataFrame({
        'age': [77, 78, 77, 79],
        'gender': [1, 1, 1, 1],
        'injury': [1, 1, 1, 1],
        'primary_dx_code': ['S2244', 'M5410', 'M7918', 'G20'],
        'disposition_type': [1, 1, 1, 2]
    })
    
    diagnosis_freq = similar_patients['primary_dx_code'].value_counts().nlargest(4)
    top_diagnoses = diagnoses_df[diagnoses_df['primary_dx_code'].isin(diagnosis_freq.index)]['primary_dx_name'].unique()
    
    disposition_modes = similar_patients['disposition_type'].value_counts(normalize=True)
    likely_disposition = disposition_modes.idxmax()
    
    print("Top 4 Most Likely Diagnoses:")
    for dx in top_diagnoses:
        print(f"- {dx}")
    
    disposition_map = {0: "Discharge", 1: "Ward Admission", 2: "ICU Admission"}
    print(f"\nPredicted Disposition Level: {disposition_map[likely_disposition]}")

patient_info = {
    'age': 77,
    'gender': 1,  # Male
    'injury': 1   # Trauma/Fall
}

predict_diagnoses_and_disposition(patient_info)