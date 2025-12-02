import pandas as pd
import numpy as np

# Load the patient data
df = pd.read_csv('patient_data.csv')

# Filter data for elderly male patients with rib fractures and shoulder issues after a fall
relevant_cases_df = df[
    (df['age'] > 65) & 
    (df['gender'] == 1) & 
    (df['primary_dx_name'].str.contains('rib fracture|shoulder', case=False, na=False))
]

# Top four common diagnoses for similar presentations
common_diagnoses = relevant_cases_df['primary_dx_name'].value_counts().head(4)
print("Top 4 Most Likely Diagnoses:")
print(common_diagnoses)

# Predict disposition level considering pulmonary and shoulder complications risk
# Calculate percentages for disposition types for filtered cases
disposition_counts = relevant_cases_df['disposition_type'].value_counts(normalize=True) * 100

predicted_disposition = disposition_counts.idxmax()
predicted_disposition_percentage = disposition_counts.max()

disposition_map = {0: 'Discharge', 1: 'Ward Admission', 2: 'ICU Admission'}

print("\nPredicted Disposition Level:")
print(f"{disposition_map[predicted_disposition]} ({predicted_disposition_percentage:.2f}%)")