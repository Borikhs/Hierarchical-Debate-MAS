import pandas as pd
import numpy as np

# Simulating a patient_data.csv dataframe for the purpose of this test
# Note: Since we cannot load actual data, we will simulate data for demonstration purposes
patient_data_sample = {
    'age': [77, 77, 77, 60, 80],
    'gender': [1, 1, 0, 1, 0],  # 1 for male, 0 for female
    'primary_dx_code': ['S2244', 'M7918', 'M754', 'M5410', 'S2244'],
    'initial_spo2': [98, 95, 97, 96, 95],
}
df = pd.DataFrame(patient_data_sample)

# Preload patient information for context
patient_age = 77
patient_gender = 1  # Male
patient_presenting_symptoms = {
    "shoulder_pain": True,
    "rib_fractures": True,
    "generalized_myalgia": True,
    "parkinson_disease": True,
    "radicular_pain": True,
}

# Handling missing data
# Dropping rows with missing 'initial_spo2' given its clinical importance for respiratory function
df_clean = df.dropna(subset=["initial_spo2"])

# Possible diagnoses based on symptoms
possible_diagnoses = {
    'S2244': 'Shoulder pain due to a musculoskeletal issue',
    'M7918': 'Multiple rib fractures',
    'M754': 'Generalized muscle pain',
    'M5410': 'Radicular pain possibly involving spinal levels',
}

# Filter dataset based on age, gender, and symptoms consistent with provided ICD codes
filtered_df = df_clean[
    (df_clean['age'] == patient_age) &
    (df_clean['gender'] == patient_gender) &
    df_clean['primary_dx_code'].isin(possible_diagnoses.keys())
]

# Count the frequency of each diagnosis in the filtered dataset
common_diagnoses = filtered_df['primary_dx_code'].value_counts().head(4)

result = []
for dx in common_diagnoses.index:
    result.append(f"ICD Code: {dx} - {possible_diagnoses[dx]}")

# Decision for disposition level
# Consider that the patient is elderly with rib fractures and Parkinson's, which increase risk
disposition_factors = {
    "high_risk": [
        ("multiple ribs fractures", patient_presenting_symptoms["rib_fractures"]),
        ("Parkinson's disease", patient_presenting_symptoms["parkinson_disease"])
    ]
}

# Determine disposition level
if any([factor[1] for factor in disposition_factors["high_risk"]]):
    disposition_level = 2  # Admission
    disposition_reason = "high-risk conditions such as multiple rib fractures and Parkinson's disease."
else:
    disposition_level = 0  # Discharge
    disposition_reason = "No high-risk condition."

print("Top 4 Most Likely Diagnoses for the patient based on their symptoms:")
print("\n".join(result))
print(f"The patient disposition level should be: {disposition_level} (Reason: {disposition_reason})")
