# -*- coding: utf-8 -*-
import pandas as pd
import sys

# 기본정보
df_basic = pd.read_excel('Data/201801-201803_1_기본정보.xlsx')
patient = df_basic.iloc[0]
patient_id = patient.iloc[0]

print(f"Processing patient: {patient_id}")

# 진단명
print("Loading diagnosis...")
df_diagnosis = pd.read_excel('Data/201801-201803_2_진단명.xlsx')
patient_diag = df_diagnosis[df_diagnosis.iloc[:, 0] == patient_id]

# 활력징후
print("Loading vital signs...")
df_vitals = pd.read_excel('Data/201801-201803_13_활력징후.xlsx')
patient_vitals = df_vitals[df_vitals.iloc[:, 0] == patient_id]

# 약품
print("Loading medications...")
df_meds = pd.read_excel('Data/201801-201803_4_약품.xlsx')
patient_meds = df_meds[df_meds.iloc[:, 0] == patient_id]

print("Creating clinical note...")

# 기본 정보
birth_year = int(str(patient.iloc[3])[:4])
age = 2018 - birth_year
gender = patient.iloc[2]
arrival_time = str(patient.iloc[8]).split()[1][:5] if ' ' in str(patient.iloc[8]) else '13:45'
arrival_method = patient.iloc[7]
esi_level = patient.iloc[4]
disposition = patient.iloc[10]

# Clinical Note 작성
note = f"""=== ED Clinical Note ===

[PATIENT INFO]
ID: {patient_id} | Age: {age}{gender} | Arrival: {arrival_time} via {arrival_method}

[TRIAGE]
CC: 응급실 내원
ESI: Level {esi_level}
"""

# 활력징후
if not patient_vitals.empty:
    vital = patient_vitals.iloc[0]
    vs_parts = []

    # 혈압, 맥박, 호흡, 체온, 산소포화도 찾기
    for i in range(len(vital)):
        val = vital.iloc[i]
        if pd.notna(val) and isinstance(val, (int, float)):
            if 100 <= val <= 200:
                vs_parts.append(f"BP {int(val)}")
            elif 30 <= val <= 150:
                vs_parts.append(f"HR {int(val)}")
            elif 10 <= val <= 40:
                vs_parts.append(f"RR {int(val)}")
            elif 90 <= val <= 100:
                vs_parts.append(f"SpO2 {int(val)}%")

    if vs_parts:
        note += f"VS: {', '.join(vs_parts[:5])}\n"
else:
    note += "VS: 활력징후 데이터 확인 필요\n"

note += "\n[HISTORY]\n"
note += "PMHx: 과거력 확인 필요\n"
note += "Allergies: 알러지 확인 필요\n"

note += f"\n[PRESENTATION]\n"
note += f"{age}yo {gender} presents to ED via {arrival_method}.\n"

note += "\n[PHYSICAL EXAM]\n"
note += "Gen: 초기 평가 참조\n"
note += "Vital signs documented at triage\n"

note += "\n[ED COURSE]\n"

# 약품 정보
if not patient_meds.empty:
    note += "Rx:\n"
    for idx, med in patient_meds.head(5).iterrows():
        # 약품명 찾기 (보통 2-4번째 컬럼에 있음)
        med_info = []
        for i in range(1, min(5, len(med))):
            val = med.iloc[i]
            if pd.notna(val) and isinstance(val, str) and len(str(val)) > 2:
                med_info.append(str(val))

        if med_info:
            note += f"  {' / '.join(med_info[:2])}\n"
else:
    note += "Rx: 투여약물 기록 참조\n"

note += "\n[DIAGNOSIS]\n"

# 진단명
if not patient_diag.empty:
    for idx, diag in patient_diag.iterrows():
        # 진단명 찾기
        diag_info = []
        for i in range(1, min(4, len(diag))):
            val = diag.iloc[i]
            if pd.notna(val) and isinstance(val, str):
                diag_info.append(str(val))

        if diag_info:
            note += f"{' - '.join(diag_info[:2])}\n"
else:
    note += "진단명 확인 필요\n"

note += f"\n[DISPOSITION]\n"
note += f"→ {disposition}\n"

note += "\n==================================================\n"

print(note)

# 파일로 저장
with open('Detailed_Clinical_Note.txt', 'w', encoding='utf-8') as f:
    f.write(note)

print("\n저장 완료: Detailed_Clinical_Note.txt")
