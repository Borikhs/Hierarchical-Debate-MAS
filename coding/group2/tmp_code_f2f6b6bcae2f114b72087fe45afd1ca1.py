def predict_diagnosis_and_disposition(age, gender, symptoms, medical_history, vital_signs, esi_level, physical_exam):
    # Initialize lists to store diagnostic and disposition predictors
    diagnosis_parts = []
    
    # Debug checks with print statements for verification
    print(f"Checking symptoms: {symptoms}")
    print(f"Medical history: {medical_history}")

    # Analyze symptoms and medical history for probable diagnosis
    if any(item in symptoms for item in ["multiple rib fractures", "severe shoulder pain"]):
        diagnosis_parts.append("Rib Fractures with Shoulder Impingement and Radiculopathy")
    if "Parkinson’s Disease" in medical_history:
        diagnosis_parts.append("Exacerbation of Parkinson's Symptoms likely")
    
    # Diagnoses debug confirmation
    print(f"Diagnoses identified: {diagnosis_parts}")
    
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

# Run the improved prediction algorithm including debug information
result = predict_diagnosis_and_disposition(age, gender, symptoms, medical_history, vital_signs, esi_level, physical_exam)
print(f"Predicted Diagnosis: {result['Diagnosis']}")
print(f"Predicted Disposition: {result['Disposition']}")