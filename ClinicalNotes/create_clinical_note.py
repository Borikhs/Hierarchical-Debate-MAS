# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import io

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 기본정보 읽기
df_basic = pd.read_excel('Data/201801-201803_1_기본정보.xlsx')

# 첫 번째 환자 선택 (인덱스 0)
patient_basic = df_basic.iloc[0]
target_patient_id = patient_basic.iloc[0]  # 첫 번째 컬럼이 환자 ID

# 2. 진단명 읽기
df_diagnosis = pd.read_excel('Data/201801-201803_2_진단명.xlsx')
patient_diagnosis = df_diagnosis[df_diagnosis['응급센터 환자 ID'] == target_patient_id]

# 3. 초기간호기록 읽기
df_initial_nursing = pd.read_excel('Data/201801-201803_10_초기간호기록.xlsx')
patient_nursing = df_initial_nursing[df_initial_nursing['응급센터 환자 ID'] == target_patient_id]

# 4. 활력징후 읽기
df_vitals = pd.read_excel('Data/201801-201803_13_활력징후.xlsx')
patient_vitals = df_vitals[df_vitals['응급센터 환자 ID'] == target_patient_id]

# 5. 진료기록 읽기
df_medical_record = pd.read_excel('Data/201801-201803_5_진료기록.xlsx')
patient_medical = df_medical_record[df_medical_record['응급센터 환자 ID'] == target_patient_id]

# 6. 약품 읽기
df_medication = pd.read_excel('Data/201801-201803_4_약품.xlsx')
patient_medication = df_medication[df_medication['응급센터 환자 ID'] == target_patient_id]

# 7. 진단검사 읽기
df_lab = pd.read_excel('Data/201801-201803_7_진단검사.xlsx')
patient_lab = df_lab[df_lab['응급센터 환자 ID'] == target_patient_id]

# 8. 영상검사 읽기
df_imaging = pd.read_excel('Data/201801-201803_8_영상검사.xlsx')
patient_imaging = df_imaging[df_imaging['응급센터 환자 ID'] == target_patient_id]

# Clinical Note 작성
print("=== ED Clinical Note ===\n")

# [PATIENT INFO]
print("[PATIENT INFO]")
age = 2018 - int(str(patient_basic['생년월일'])[:4])
gender = patient_basic['성별']
arrival_time = str(patient_basic['내원일시기록시간']).split()[1][:5] if len(str(patient_basic['내원일시기록시간']).split()) > 1 else ""
arrival_method = patient_basic['내원수단']
print(f"ID: {patient_basic['응급센터 환자 ID']} | Age: {age}{gender} | Arrival: {arrival_time} via {arrival_method}")
print()

# [TRIAGE]
print("[TRIAGE]")
if not patient_nursing.empty:
    cc = patient_nursing.iloc[0].get('주증상', 'N/A') if '주증상' in patient_nursing.columns else 'N/A'
    print(f"CC: {cc}")
    esi_level = patient_basic.get('응급환자분류코드', 'N/A')
    print(f"ESI: Level {esi_level}")

# 첫 번째 활력징후 가져오기
if not patient_vitals.empty:
    first_vital = patient_vitals.iloc[0]
    bp_sys = first_vital.get('수축기혈압', 'N/A')
    bp_dia = first_vital.get('이완기혈압', 'N/A')
    hr = first_vital.get('맥박수', 'N/A')
    rr = first_vital.get('호흡수', 'N/A')
    temp = first_vital.get('체온', 'N/A')
    spo2 = first_vital.get('산소포화도', 'N/A')

    vs_str = f"VS: BP {bp_sys}/{bp_dia}" if pd.notna(bp_sys) and pd.notna(bp_dia) else "VS: BP N/A"
    if pd.notna(hr):
        vs_str += f", HR {int(hr)}"
    if pd.notna(rr):
        vs_str += f", RR {int(rr)}"
    if pd.notna(temp):
        vs_str += f", T {temp}°C"
    if pd.notna(spo2):
        vs_str += f", SpO2 {int(spo2)}%"

    print(vs_str)
print()

# [HISTORY]
print("[HISTORY]")
if not patient_nursing.empty:
    nursing_rec = patient_nursing.iloc[0]
    # 과거력, 현재 복용약, 알레르기 등
    pmhx = nursing_rec.get('과거력', 'N/A') if '과거력' in patient_nursing.columns else 'N/A'
    allergy = nursing_rec.get('알러지', 'None') if '알러지' in patient_nursing.columns else 'None'

    print(f"PMHx: {pmhx}")
    print(f"Allergies: {allergy}")
print()

# [PRESENTATION]
print("[PRESENTATION]")
if not patient_nursing.empty:
    cc_detail = patient_nursing.iloc[0].get('주증상상세', '') if '주증상상세' in patient_nursing.columns else ''
    onset = patient_nursing.iloc[0].get('발병일시', '') if '발병일시' in patient_nursing.columns else ''

    presentation = f"{age}yo {gender}"
    if pd.notna(pmhx) and pmhx != 'N/A':
        presentation += f" with {pmhx}"
    presentation += f" presents with {cc if pd.notna(cc) else 'chief complaint'}."
    if pd.notna(cc_detail):
        presentation += f" {cc_detail}"

    print(presentation)
print()

# [PHYSICAL EXAM]
print("[PHYSICAL EXAM]")
if not patient_nursing.empty:
    exam_findings = []

    # 의식 상태
    mental = patient_nursing.iloc[0].get('의식상태', '') if '의식상태' in patient_nursing.columns else ''
    if pd.notna(mental):
        exam_findings.append(f"Gen: {mental}")

    # 호흡음
    breath_sound = patient_nursing.iloc[0].get('호흡음', '') if '호흡음' in patient_nursing.columns else ''
    if pd.notna(breath_sound):
        exam_findings.append(f"Resp: {breath_sound}")

    for finding in exam_findings:
        print(finding)
print()

# [ED COURSE]
print("[ED COURSE]")

# Labs
if not patient_lab.empty:
    print("Labs:")
    for idx, lab in patient_lab.head(5).iterrows():
        test_name = lab.get('검사명', '')
        result = lab.get('검사결과', '')
        unit = lab.get('단위', '')

        if pd.notna(test_name) and pd.notna(result):
            print(f"  {test_name}: {result} {unit if pd.notna(unit) else ''}")

# Imaging
if not patient_imaging.empty:
    print("\nImaging:")
    for idx, img in patient_imaging.iterrows():
        exam_name = img.get('검사명', '')
        if pd.notna(exam_name):
            print(f"  {exam_name}")

# Medications
if not patient_medication.empty:
    print("\nRx:")
    for idx, med in patient_medication.head(5).iterrows():
        med_name = med.get('약품명', '')
        dose = med.get('투여량', '')
        route = med.get('투여경로', '')

        if pd.notna(med_name):
            med_str = f"  {med_name}"
            if pd.notna(dose):
                med_str += f" {dose}"
            if pd.notna(route):
                med_str += f" {route}"
            print(med_str)

print()

# [DIAGNOSIS]
print("[DIAGNOSIS]")
if not patient_diagnosis.empty:
    for idx, diag in patient_diagnosis.iterrows():
        diag_name = diag.get('진단명', '')
        if pd.notna(diag_name):
            print(diag_name)
print()

# [DISPOSITION]
print("[DISPOSITION]")
disposition = patient_basic.get('최종결과명', 'N/A')
print(f"→ {disposition}")
if not patient_medical.empty and '진료기록' in patient_medical.columns:
    medical_note = patient_medical.iloc[0]['진료기록']
    if pd.notna(medical_note):
        print(f"Reason: {str(medical_note)[:200]}")

print("\n" + "="*50)
