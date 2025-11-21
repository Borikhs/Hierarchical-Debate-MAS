def predict_diagnosis_and_disposition(age, gender, symptoms, medical_history, vital_signs, esi_level, physical_exam):
    # Initialize empty list to store diagnosis predictions
    diagnosis_parts = []
    
    # Analyze symptoms and medical history for probable diagnosis
    if "rib fractures" in symptoms and "shoulder impingement" in symptoms:
        diagnosis_parts.append("Rib Fractures with Shoulder Impingement and Radiculopathy")
    if "Parkinson’s Disease" in medical_history:
        diagnosis_parts.append("Exacerbation of Parkinson's Symptoms likely")
    
    # Join diagnosis parts to form full diagnosis string
    predictions_diagnosis = ", ".join(diagnosis_parts)
    
    # Initialize disposition
    disposition = ""
    
    # Determine disposition based on ESI level and clinical presentation
    if esi_level == "ESI Level 1":
        disposition = "Admission for monitoring and pain management"
    
    # Check vital signs for additional concerns
    if vital_signs.get("Temperature", 36.5) >= 38.0:
        disposition += " with focus on Infection Control"
        
    # Adjust for any additional observations from the physical exam
    if "mild discomfort" in physical_exam.get("Neurological", ""):
        disposition += " and neurological monitoring"
    
    # Return combined predictions
    return {
        "Diagnosis": predictions_diagnosis,
        "Disposition": disposition
    }

# Run the improved prediction algorithm
age = 78
gender = "Female"
symptoms = ["severe shoulder pain", "multiple rib fractures", "generalized muscle aches"]
medical_history = ["Parkinson’s Disease", "History of multiple minor falls"]
vital_signs = {"Temperature": 36.5, "Respiratory Rate": 18, "Heart Rate": 89}
esi_level = "ESI Level 1"
physical_exam = {
    "General": "Alert, oriented, mildly diaphoretic due to pain",
    "Musculoskeletal": "Tenderness over shoulder area, multiple tender points on rib cage",
    "Neurological": "Mild discomfort in upper extremity"
}

result = predict_diagnosis_and_disposition(age, gender, symptoms, medical_history, vital_signs, esi_level, physical_exam)
print(f"Predicted Diagnosis: {result['Diagnosis']}")
print(f"Predicted Disposition: {result['Disposition']}")