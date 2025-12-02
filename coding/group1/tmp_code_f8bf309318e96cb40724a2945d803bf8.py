import pandas as pd

# Load patient data
df = pd.read_csv('patient_data.csv')

# Filter dataset for elderly males with rib fractures related injury
elderly_males_injury = df[(df['age'] > 65) & (df['gender'] == 1) & (df['injury'] == 1)]

# Consider patients with similar injury presentation
similar_injury_patients = elderly_males_injury[
    (elderly_males_injury['triage_level'] <= 2) &
    (elderly_males_injury['primary_dx_name'].str.contains('rib', case=False, na=False))
]

# Rankings of diagnoses based on frequency
top_diagnoses = similar_injury_patients['primary_dx_name'].value_counts().nlargest(4)
print("Most Likely Diagnoses for Similar Injury Presentation:")
print(top_diagnoses)

# Determining disposition level for similar cases
disposition_counts = similar_injury_patients['disposition_type'].value_counts(normalize=True) * 100
disposition_map = {0: 'Discharge', 1: 'Ward Admission', 2: 'ICU Admission'}

# Displaying the results
print("\nPredicted Disposition Levels:")
for disp, perc in disposition_counts.items():
    print(f"{disposition_map[disp]}: {perc:.2f}%")