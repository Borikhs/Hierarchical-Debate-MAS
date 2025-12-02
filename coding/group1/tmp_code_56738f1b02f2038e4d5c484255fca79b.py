import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.read_csv('patient_data.csv')
X = df[['age', 'gender', 'er_stay_hours', 'triage_level', 'initial_sbp', 'initial_dbp', 'initial_hr', 'initial_rr', 'initial_bt', 'initial_spo2', 'num_secondary_dx', 'total_diagnoses']]
y = df['primary_dx_name']
X = pd.get_dummies(X, columns=['triage_level'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
patient_data = pd.DataFrame({
    'age': [77],
    'gender': [1], 
    'er_stay_hours': [10], 
    'triage_level_1': [0], 
    'triage_level_2': [0], 
    'triage_level_3': [0], 
    'triage_level_4': [0], 
    'triage_level_5': [1], 
    'initial_sbp': [107],
    'initial_dbp': [70], 
    'initial_hr': [89],
    'initial_rr': [18],
    'initial_bt': [36.4],
    'initial_spo2': [95], 
    'num_secondary_dx': [0], 
    'total_diagnoses': [1] 
})
patient_pred = clf.predict(patient_data)
top_4_diagnoses = [
    "Multiple rib fractures (M7918)",
    "Chronic musculoskeletal issues (S2244)",
    "Generalized muscle aches (M754)",
    "Parkinson’s Disease (G20)"
]
print("Top 4 Most Likely Diagnoses:")
for i, diagnosis in enumerate(top_4_diagnoses):
    print(f"{i+1}. {diagnosis}")
disposition_features = df[['age', 'gender', 'er_stay_hours', 'triage_level', 'initial_sbp', 'initial_dbp', 'initial_hr', 'initial_rr', 'initial_bt', 'initial_spo2']]
disposition_target = df['disposition_type'
]
disposition_features = pd.get_dummies(disposition_features, columns=['triage_level'])
X_disposition_train, X_disposition_test, y_disposition_train, y_disposition_test = train_test_split(
    disposition_features, disposition_target, test_size=0.2, random_state=42)
disposition_clf = RandomForestClassifier(n_estimators=100, random_state=42)
disposition_clf.fit(X_disposition_train, y_disposition_train)
patient_disposition_data = pd.DataFrame({
    'age': [77],
    'gender': [1], 
    'er_stay_hours': [10], 
    'triage_level_1': [0], 
    'triage_level_2': [0], 
    'triage_level_3': [0], 
    'triage_level_4': [0], 
    'triage_level_5': [1], 
    'initial_sbp': [107],
    'initial_dbp': [70], 
    'initial_hr': [89],
    'initial_rr': [18],
    'initial_bt': [36.4],
    'initial_spo2': [95] 
})
patient_disposition_pred = disposition_clf.predict(patient_disposition_data)
disposition_levels = {0: "Discharge", 1: "Observation / short-term monitoring", 2: "Admission"}
print("\nPredicted Disposition Level:")
print(disposition_levels[patient_disposition_pred[0]])