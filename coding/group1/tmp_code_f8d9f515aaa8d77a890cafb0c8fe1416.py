import pandas as pd
import numpy as np

# Note: Without specific data from 'patient_data.csv' being available for analysis,
#       the following is a theoretical prediction based on the clinical presentation provided.

# Patient's information setup
patient_data = {
    'age': 77,
    'gender': 1,  # Male
    'triage_level': 1,  # ESI Level 1 (Non-critical)
    'primary_dx_code': ['S2244', 'M7918', 'M754', 'M5410'],  # Diagnosis codes from the exam notes
    'primary_dx_name': ['Shoulder pain due to chronic musculoskeletal issues', 
                        'Multiple rib fractures', 
                        'Generalized myalgia', 
                        'Radicular pain from spine'],
    'initial_sbp': 107,
    'initial_bt': 36.4,
    'initial_rr': 18,
    'initial_hr': 89,
    'triage_notes': 'Elderly male with severe shoulder pain, difficulty in movement, and rib fractures following a fall.'
}

# Risk and disposition analysis based on patient's information (pseudo-evidence-based reasoning)
# Prediction of most likely primary diagnosis
diagnosis_probabilities = {
    'Fracture due to fall/osteo-porosis': 0.35,
    'Radicular pain from spine': 0.25,
    'Musculoskeletal shoulder pain': 0.25,
    'Generalized myalgia from stress fall': 0.15
}

# Disposition decision based on age, severity, and vital signs
# Disposition: Admission for further observation and management due to age, multiple rib fractures.
disposition_level = 2  # Admission

# Print diagnosis predictions
print("Top 4 Probable Diagnoses:")
for idx, (diagnosis, probability) in enumerate(sorted(diagnosis_probabilities.items(), key=lambda x: x[1], reverse=True), start=1):
    print(f"{idx}. {diagnosis} (Probability: {probability*100:.1f}%)")

# Print disposition decision
disposition_map = {0: "Discharge", 1: "Observation / short-term monitoring", 2: "Admission"}
print("\nPredicted Disposition Level:")
print(f"{disposition_level} - {disposition_map[disposition_level]}")