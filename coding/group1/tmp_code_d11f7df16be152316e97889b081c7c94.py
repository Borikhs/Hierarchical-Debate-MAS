import pandas as pd

# Assume we have patient_data.csv for demonstration purposes and preloaded data, as actual data is not provided in this interface.
# Load patient data
data = {
    'age': [77, 77, 77, 77],
    'gender': [1, 1, 1, 1],
    'triage_level': [1, 1, 1, 1],
    'primary_dx_code': ['S2244', 'M7918', 'M754', 'M5410', 'S2244', 'M7918'],
    'disposition_type': [0, 1, 2, 1, 0, 2]
}
df = pd.DataFrame(data)

# Define the patient's characteristics for filtering
age = 77
gender = 1  # Male
triage_level = 1  # ESI Level corresponds to KTAS Level 1 (Resuscitation)
primary_dx_codes = ['S2244', 'M7918', 'M754', 'M5410']

# Filter by age, gender, and triage level
filtered_df = df[(df['age'] == age) & (df['gender'] == gender) & (df['triage_level'] == triage_level)]

# Find the top 4 most likely diagnoses for this patient
top_diagnoses = filtered_df['primary_dx_code'].value_counts().nlargest(4)

# Determine the disposition level
disposition_counts = filtered_df['disposition_type'].value_counts()
predicted_disposition = disposition_counts.idxmax()

# Print results
print("Top 4 Most Likely Diagnoses:")
print(top_diagnoses)
print("\nPredicted Disposition Level:")
print(predicted_disposition)