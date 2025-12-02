import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('patient_data.csv')

# Define conditions and symptoms from the patient information
conditions = [
    "Parkinson’s Disease", 
    "chronic musculoskeletal issues", 
    "rib fractures", 
    "myalgia"
]

symptoms = [
    "severe shoulder pain", 
    "rib fractures", 
    "myalgia", 
    "fall", 
    "muscle aches", 
    "radicular pain"
]

# ICD-10 codes associated with the conditions
icd10_codes = {
    "S2244": "Multiple rib fractures",
    "M7918": "Myalgia",
    "M754": "Chronic myalgia",
    "M5410": "Radicular pain",
    "G20": "Parkinson's Disease"
}

# Filter the dataset by relevant diagnoses
related_diag_codes = df[df['primary_dx_code'].isin(icd10_codes.keys())]

# Calculate the most common primary diagnoses based on symptom presentation
most_likely_diagnoses = related_diag_codes['primary_dx_name'].value_counts().nlargest(4)

# Predict disposition level based on medical criteria and patient history
def predict_disposition(age, esi_level, rib_fractures, chronic_condition):
    # Age above 75 and presence of severe injuries such as rib fractures
    # along with chronic conditions like Parkinson's suggests monitoring or admission
    if age > 75 and (rib_fractures > 0) and chronic_condition:
        if esi_level == 1:
            return 2  # Admission
        else:
            return 1  # Observation / short-term monitoring
    return 0  # Discharge if none of the above

# Predict disposition for this specific patient
age = 77
esi_level = 1  # ESI Level is 1, non-critical
rib_fractures = int('S2244' in conditions)
chronic_condition = int('G20' in conditions)

patient_disposition = predict_disposition(age, esi_level, rib_fractures, chronic_condition)

# Print the top 4 most likely diagnoses and disposition prediction
print("Top 4 Most Likely Diagnoses:")
for idx, diag in enumerate(most_likely_diagnoses.index, 1):
    print(f"{idx}. {diag}")

disposition_map = {0: "Discharge", 1: "Observation / short-term monitoring", 2: "Admission"}
print("\nPredicted Disposition Level:")
print(disposition_map[patient_disposition])