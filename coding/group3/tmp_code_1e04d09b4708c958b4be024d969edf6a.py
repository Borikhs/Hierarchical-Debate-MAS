def predict_diagnosis_and_disposition(patient_info):
    try:
        # Extract essential patient info
        age = patient_info['Age']
        symptom_description = patient_info['Clinical Presentation']['Chief Complaint']
        past_medical_history = patient_info['Medical History']['Past Medical History']

        # Basic diagnosis based on symptoms and medical history
        diagnosis = []
        if 'shoulder pain' in symptom_description.lower():
            diagnosis.append('Shoulder Impingement Syndrome')
        if 'rib fracture' in symptom_description.lower():
            diagnosis.append('Multiple Rib Fractures')

        if age >= 65:
            if 'parkinson' in past_medical_history.lower():
                diagnosis.append('Exacerbation of Parkinson’s Disease symptoms due to injury')

        # Disposition suggestion based on severity and conditions
        if 'fall' in symptom_description.lower():
            disposition = 'Admit for observation and further imaging'
        else:
            disposition = 'Refer to outpatient orthopedic and neurology'

        return diagnosis, disposition

    except Exception as e:
        return str(e)

# Mock patient info based on provided data
patient_info = {
    'Age': 78,
    'Clinical Presentation': {
        'Chief Complaint': 'Severe shoulder pain with limitation in movement due to multiple rib fractures.'
    },
    'Medical History': {
        'Past Medical History': 'Parkinson’s Disease'
    }
}

# Use the function to get diagnosis and disposition
diagnosis, disposition = predict_diagnosis_and_disposition(patient_info)
print(f"Predicted Diagnosis: {diagnosis}")
print(f"Suggested Disposition: {disposition}")