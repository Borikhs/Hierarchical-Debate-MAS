import pandas as pd

# Load the patient data
df = pd.read_csv('patient_data.csv')

# Filter out any missing diagnosis data
df_clean = df.dropna(subset=['primary_dx_name', 'primary_dx_code'])

# Collect statistical data on diagnosis given the patient's profile
# Define patient's age, gender, and injury type for filtering data
patient_age = 77
patient_gender = 1  # Male
patient_injury = 1  # Trauma due to fall

# Filter data based on gender, age over 65, and injury type as trauma
relevant_patients = df_clean[(df_clean['age'] >= 65) & 
                             (df_clean['gender'] == patient_gender) & 
                             (df_clean['injury'] == patient_injury)]

# Group by diagnosis name to find the most common diagnoses 
top_diagnoses = relevant_patients['primary_dx_name'].value_counts().head(4)
print("Top 4 Most Likely Diagnoses Based on Patient Profile:")
print(top_diagnoses)

# Analyze disposition type (using provided levels: 0=Discharge, 1=Observation, 2=Admission)
disposition_counts = relevant_patients['disposition_type'].value_counts(normalize=True) * 100
disposition_levels = ["Discharge", "Observation", "Admission"]

print("\nDisposition Level Probabilities (in percentage):")
for disposition_type, percentage in disposition_counts.items():
    print(f"{disposition_levels[disposition_type]}: {percentage:.2f}%")

# Since the patient presented with severe symptoms and is ESI Level 1 (Non-critical), 
# they are likely to be kept for observation or admitted based on the statistical analysis
