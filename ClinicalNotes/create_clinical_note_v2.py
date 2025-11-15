# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import sys

# 1. 기본정보 읽기
df_basic = pd.read_excel('Data/201801-201803_1_기본정보.xlsx')

# 첫 번째 환자 선택
patient_basic = df_basic.iloc[0]
target_patient_id = patient_basic.iloc[0]  # 응급센터 환자 ID

print(f"Target Patient ID: {target_patient_id}\n")

# 2. 다른 데이터 읽기 (첫 번째 컬럼으로 필터링)
df_diagnosis = pd.read_excel('Data/201801-201803_2_진단명.xlsx')
patient_diagnosis = df_diagnosis[df_diagnosis.iloc[:, 0] == target_patient_id]

df_initial_nursing = pd.read_excel('Data/201801-201803_10_초기간호기록.xlsx')
patient_nursing = df_initial_nursing[df_initial_nursing.iloc[:, 0] == target_patient_id]

df_vitals = pd.read_excel('Data/201801-201803_13_활력징후.xlsx')
patient_vitals = df_vitals[df_vitals.iloc[:, 0] == target_patient_id]

df_medical_record = pd.read_excel('Data/201801-201803_5_진료기록.xlsx')
patient_medical = df_medical_record[df_medical_record.iloc[:, 0] == target_patient_id]

df_medication = pd.read_excel('Data/201801-201803_4_약품.xlsx')
patient_medication = df_medication[df_medication.iloc[:, 0] == target_patient_id]

df_lab = pd.read_excel('Data/201801-201803_7_진단검사.xlsx')
patient_lab = df_lab[df_lab.iloc[:, 0] == target_patient_id]

df_imaging = pd.read_excel('Data/201801-201803_8_영상검사.xlsx')
patient_imaging = df_imaging[df_imaging.iloc[:, 0] == target_patient_id]

# Clinical Note 작성
note = []
note.append("=== ED Clinical Note ===")
note.append("")

# [PATIENT INFO]
note.append("[PATIENT INFO]")
# 컬럼 순서: ID(0), 환자명(1), 성별(2), 생년월일(3), 응급분류코드(4), 내원일자(5), 응급센터체류시간(6), 내원수단(7), 내원시기록시간(8), 내원완료시간(9), 최종결과(10)
age = 2018 - int(str(patient_basic.iloc[3])[:4])  # 생년월일
gender = patient_basic.iloc[2]  # 성별
arrival_time = str(patient_basic.iloc[8]).split()[1][:5] if len(str(patient_basic.iloc[8]).split()) > 1 else ""
arrival_method = patient_basic.iloc[7]  # 내원수단
note.append(f"ID: {target_patient_id} | Age: {age}{gender} | Arrival: {arrival_time} via {arrival_method}")
note.append("")

# [TRIAGE]
note.append("[TRIAGE]")
if not patient_nursing.empty:
    nursing_cols = patient_nursing.columns.tolist()
    cc = "주증상 정보 확인 필요"
    # ESI 레벨
    esi_level = patient_basic.iloc[4]
    note.append(f"CC: {cc}")
    note.append(f"ESI: Level {esi_level}")

# 첫 번째 활력징후
if not patient_vitals.empty:
    first_vital = patient_vitals.iloc[0]
    vital_cols = patient_vitals.columns.tolist()

    # 활력징후 데이터 찾기
    vs_parts = []
    for i, col in enumerate(vital_cols):
        if '혈압' in str(col) or 'BP' in str(col):
            val = first_vital.iloc[i]
            if pd.notna(val):
                vs_parts.append(f"BP {val}")
        elif '맥박' in str(col) or 'HR' in str(col):
            val = first_vital.iloc[i]
            if pd.notna(val):
                vs_parts.append(f"HR {int(val)}")
        elif '호흡' in str(col) or 'RR' in str(col):
            val = first_vital.iloc[i]
            if pd.notna(val):
                vs_parts.append(f"RR {int(val)}")
        elif '체온' in str(col) or 'Temp' in str(col):
            val = first_vital.iloc[i]
            if pd.notna(val):
                vs_parts.append(f"T {val}°C")
        elif '산소' in str(col) or 'SpO2' in str(col):
            val = first_vital.iloc[i]
            if pd.notna(val):
                vs_parts.append(f"SpO2 {int(val)}%")

    if vs_parts:
        note.append(f"VS: {', '.join(vs_parts)}")
note.append("")

# [HISTORY]
note.append("[HISTORY]")
note.append("PMHx: 진료기록 참조")
note.append("Allergies: 초기간호기록 참조")
note.append("")

# [PRESENTATION]
note.append("[PRESENTATION]")
presentation = f"{age}yo {gender} presents to ED"
if not patient_nursing.empty:
    presentation += " with chief complaint as documented."
note.append(presentation)
note.append("")

# [PHYSICAL EXAM]
note.append("[PHYSICAL EXAM]")
note.append("Gen: 초기간호기록 참조")
note.append("초기 평가 데이터 확인 필요")
note.append("")

# [ED COURSE]
note.append("[ED COURSE]")

# Labs
if not patient_lab.empty:
    note.append("Labs:")
    lab_cols = patient_lab.columns.tolist()
    for idx, lab in patient_lab.head(5).iterrows():
        # 검사명과 결과 찾기
        test_info = []
        for i, val in enumerate(lab):
            if pd.notna(val) and i > 0:  # ID 컬럼 제외
                test_info.append(str(val))
        if test_info:
            note.append(f"  {' - '.join(test_info[:3])}")  # 처음 3개 값만

# Imaging
if not patient_imaging.empty:
    note.append("\nImaging:")
    for idx, img in patient_imaging.head(3).iterrows():
        img_info = []
        for i, val in enumerate(img):
            if pd.notna(val) and i > 0:
                img_info.append(str(val))
        if img_info:
            note.append(f"  {' - '.join(img_info[:2])}")

# Medications
if not patient_medication.empty:
    note.append("\nRx:")
    for idx, med in patient_medication.head(5).iterrows():
        med_info = []
        for i, val in enumerate(med):
            if pd.notna(val) and i > 0:
                med_info.append(str(val))
        if med_info:
            note.append(f"  {' - '.join(med_info[:3])}")

note.append("")

# [DIAGNOSIS]
note.append("[DIAGNOSIS]")
if not patient_diagnosis.empty:
    for idx, diag in patient_diagnosis.iterrows():
        diag_info = []
        for i, val in enumerate(diag):
            if pd.notna(val) and i > 0:
                diag_info.append(str(val))
        if diag_info:
            note.append(f"{' - '.join(diag_info[:2])}")
else:
    note.append("진단명 데이터 확인 필요")
note.append("")

# [DISPOSITION]
note.append("[DISPOSITION]")
disposition = patient_basic.iloc[10]  # 최종결과명
note.append(f"→ {disposition}")
if not patient_medical.empty:
    note.append("Reason: 진료기록 참조")

note.append("")
note.append("="*50)

# 출력
output_text = "\n".join(note)
print(output_text)

# 파일로 저장
with open('Sample_Clinical_Note.txt', 'w', encoding='utf-8') as f:
    f.write(output_text)

print("\n\n저장 완료: Sample_Clinical_Note.txt")
