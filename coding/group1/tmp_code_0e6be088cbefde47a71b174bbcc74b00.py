import pandas as pd
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load patient data
df = pd.read_csv('patient_data.csv')

# Define features (X) and target variables (y)
X = df[['age', 'gender', 'er_stay_hours', 'triage_level', 'initial_sbp', 'initial_dbp', 'initial_hr', 'initial_rr', 'initial_bt', 'initial_spo2']]
y_diagnosis = df['primary_dx_name'
]
y_disposition = df['disposition_type'
]

# Split data into training and testing sets
X_train, X_test, y_train_diagnosis, y_test_diagnosis = train_test_split(X, y_diagnosis, test_size=0.2, random_state=42)
X_train, X_test, y_train_disposition, y_test_disposition = train_test_split(X, y_disposition, test_size=0.2, random_state=42)

# Train a random forest classifier for diagnosis prediction
rf_diagnosis = RandomForestClassifier(n_estimators=100, random_state=42)
rf_diagnosis.fit(X_train, y_train_diagnosis)

# Predict the top 4 most likely diagnoses for the patient
patient_data = pd.DataFrame({
    'age': [77],
    'gender': [1],  # Male
    'er_stay_hours': [0],  # Assume unknown
    'triage_level': [2],  # Emergent
    'initial_sbp': [107],  # Systolic blood pressure
    'initial_dbp': [70],  # Diastolic blood pressure (unknown, assume normal)
    'initial_hr': [89],  # Heart rate
    'initial_rr': [18],  # Respiratory rate
    'initial_bt': [36.4],  # Body temperature
    'initial_spo2': [95]  # Oxygen saturation (unknown, assume normal)
})

predicted_diagnoses = rf_diagnosis.predict_proba(patient_data)
top_4_diagnoses = sorted(zip(rf_diagnosis.classes_, predicted_diagnoses[0]), key=lambda x: x[1], reverse=True)[:4]

print("Top 4 most likely diagnoses:")
for diagnosis, probability in top_4_diagnoses:
    print(f"{diagnosis}: {probability * 100:.2f}%")

# Train a random forest classifier for disposition level prediction
rf_disposition = RandomForestClassifier(n_estimators=100, random_state=42)
rf_disposition.fit(X_train, y_train_disposition)

# Predict the disposition level for the patient
predicted_disposition = rf_disposition.predict(patient_data)
print(f"\nPredicted disposition level: {predicted_disposition[0]}")

disposition_map = {0: 'Discharge', 1: 'Observation / short-term monitoring', 2: 'Admission'}
print(f"Disposition level: {disposition_map[predicted_disposition[0]]}")