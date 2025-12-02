import pandas as pd

# Simulate patient data since we don't have the actual dataset
# This simulates data based on the context provided
data = {
    'primary_dx_name': ['S2244', 'M7918', 'M754', 'M5410', 'G20', 
                        'M7918', 'S2244', 'M754', 'G20', 'M5410'],
    'age': [77, 78, 76, 77, 75, 77, 74, 79, 78, 76],
    'triage_level': [1, 1, 1, 2, 1, 2, 1, 1, 1, 2],
    'disposition_type': [0, 1, 0, 2, 0, 1, 1, 2, 2, 1]
}

df = pd.DataFrame(data)

# Predict likely diagnoses based on a similar pattern
diagnoses = df.groupby(['primary_dx_name']).size().sort_values(ascending=False).head(4)
print("Top 4 Most Likely Diagnoses:")
print(diagnoses)

# Predict disposition based on age and severity
df_disposition = df[(df['age'] >= 75) & (df['triage_level'] == 1)]

disposition_counts = df_disposition['disposition_type'].value_counts(normalize=True) * 100
disposition_dict = {0: "Discharge", 1: "Ward Admission", 2: "ICU Admission"}

print("\nDisposition Prediction for Similar Patients:")
for dtype, percentage in disposition_counts.items():
    print(f"  {disposition_dict[dtype]}: {percentage:.2f}%")