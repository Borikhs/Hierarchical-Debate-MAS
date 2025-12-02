import pandas as pd

# Load patient data
df = pd.read_csv('patient_data.csv')

# Filter dataset for elderly males with injuries
elderly_males = df[(df['age'] > 65) & (df['gender'] == 1) & (df['injury'] == 1)]

# Top 4 most likely diagnoses
top_diagnoses = elderly_males['primary_dx_name'].value_counts().head(4)
print("Top 4 Most Likely Diagnoses for Elderly Male with Rib Fractures:")
print(top_diagnoses)

# Determine disposition level based on similar cases
similar_cases = elderly_males[(elderly_males['primary_dx_code'].isin(top_diagnoses.index))]
disposition_counts = similar_cases['disposition_type'].value_counts(normalize=True) * 100
disposition_map = {0: 'Discharge', 1: 'Ward Admission', 2: 'ICU Admission'}

print("\nPredicted Disposition Levels:")
for disp, perc in disposition_counts.items():
    print(f"{disposition_map[disp]}: {perc:.2f}%")