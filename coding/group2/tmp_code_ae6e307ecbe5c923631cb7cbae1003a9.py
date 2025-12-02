import pandas as pd
import numpy as np

# Simulate patient data as we don't have the actual dataset
# Simulating data based on the context
data = {
    'primary_dx_name': ['M7918', 'S2244', 'G20', 'M754', 'M5410',
                        'M7918', 'M754', 'G20', 'M5410', 'M7918'],
    'age': [77, 78, 65, 80, 60, 77, 75, 68, 85, 90],
    'disposition_type': [0, 1, 0, 1, 2, 0, 2, 2, 1, 1],
    'num_secondary_dx': [3, 2, 1, 0, 4, 2, 1, 5, 2, 1],
    'intubation': [0, 1, 0, 0, 1, 0, 1, 1, 0, 0],
    'ventilator': [0, 1, 0, 0, 1, 0, 1, 1, 0, 0],
    'vasopressor': [0, 1, 0, 0, 1, 0, 1, 1, 0, 0]
}

df = pd.DataFrame(data)

# Enhance the retrieval of similar patients for rib fracture analysis
rib_fracture_patients = df[df['primary_dx_name'] == 'M7918']

# Analyze risk factors for ICU admission based on age and diagnosis
icu_risk_patients = rib_fracture_patients[(rib_fracture_patients['age'] > 65)]
icu_risks = icu_risk_patients['disposition_type'].value_counts(normalize=True) * 100
disposition_map = {0: "Discharge", 1: "Ward Admission", 2: "ICU Admission"}

print("\nICU Admission Risk for Elderly Patients with Rib Fractures:")
for dtype, risk in icu_risks.items():
    print(f"  {disposition_map[dtype]}: {risk:.2f}%")

# Suggested disposition based on count of rib fractures
rib_fracture_severity = rib_fracture_patients['num_secondary_dx'].mean()
print(f"\nAverage Additional Diagnoses in Rib Fracture Patients: {rib_fracture_severity:.2f}")

# Explore interventions correlation with disposition
interventions = ['intubation', 'ventilator', 'vasopressor']
for intervention in interventions:
    intervention_rate = df.groupby('disposition_type')[intervention].mean() * 100
    print(f"\n{intervention.capitalize()} Use by Disposition:")
    for dtype, rate in intervention_rate.items():
        print(f"  {disposition_map[dtype]}: {rate:.2f}%")