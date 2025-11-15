# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime

# base 파일 읽기
df_base = pd.read_excel('Data/snuh_20180103_base.xlsx')

# 첫 번째 환자 선택
patient = df_base.iloc[0]

# 데이터 추출
patient_id = patient['id']
age = int(patient['age'])
sex = 'F' if patient['sex'] == 0 else 'M'
er_dt = patient['er_dt']
dc_dt = patient['dc_dt']
arrival_time = str(er_dt).split()[1][:5] if ' ' in str(er_dt) else ''

# Chief Complaint
cc = patient['cc']

# 발병 시간
onset_dt = patient['onset_dt']

# 활력징후
sbp = int(patient['init_sbp']) if pd.notna(patient['init_sbp']) else None
dbp = int(patient['init_dbp']) if pd.notna(patient['init_dbp']) else None
hr = int(patient['init_hr']) if pd.notna(patient['init_hr']) else None
rr = int(patient['init_rr']) if pd.notna(patient['init_rr']) else None
bt = patient['init_bt']
spo2 = int(patient['init_spo2']) if pd.notna(patient['init_spo2']) else None

# 의식 수준 (AVPU: 1=Alert, 2=Verbal, 3=Pain, 4=Unresponsive)
avpu_dict = {1: 'Alert', 2: 'Verbal', 3: 'Pain', 4: 'Unresponsive'}
avpu = avpu_dict.get(patient['init_avpu'], 'Unknown')

# KTAS
ktas_level = int(patient['ktas_level'])

# 진단
dx1 = patient['dx1']
dx1_name = patient['dx1_name']
dx2_1 = patient['dx2_1']
dx2_2 = patient['dx2_2']
dx2_3 = patient['dx2_3']
dx2_4 = patient['dx2_4']

# 초기 간호 기록
init_nurse_note = patient['init_nurse_note']

# 진입 방법
entry_dict = {0.0: '도보', 1.0: 'Walk-in'}
entry = entry_dict.get(patient['entry'], '도보')

# 손상 여부
injury = '있음' if patient['injury'] == 1.0 else '없음'

# EMS 사용 여부
ems = 'Yes' if patient['ems'] == 1.0 else 'No'

# 처치 정보
intubation = 'Yes' if patient['intubation'] == 1 else 'No'
ventilator = 'Yes' if patient['ventilator'] == 1 else 'No'
vasopressor = 'Yes' if patient['vasopressor'] == 1 else 'No'

# Clinical Note 작성
note = f"""=== ED Clinical Note ===

[PATIENT INFO]
ID: {patient_id}
Age: {age}{sex} | Arrival: {arrival_time}
Entry: {entry} | EMS: {ems}

[TRIAGE]
CC: {cc}
KTAS Level: {ktas_level}
Onset: {onset_dt}
"""

# 활력징후
vs_parts = []
if sbp and dbp:
    vs_parts.append(f"BP {sbp}/{dbp}")
if hr:
    vs_parts.append(f"HR {hr}")
if rr:
    vs_parts.append(f"RR {rr}")
if bt:
    vs_parts.append(f"T {bt}°C")
if spo2:
    vs_parts.append(f"SpO2 {spo2}%")

note += f"VS: {', '.join(vs_parts)}\n"
note += f"AVPU: {avpu}\n"

note += f"""
[INITIAL NURSING ASSESSMENT]
Time: {patient['init_nurse_dt']}
Note: {init_nurse_note}

[PRESENTATION]
{age}yo {sex} presents to ED with {cc}.
Onset: {onset_dt}
Injury: {injury}

[PHYSICAL EXAM]
Gen: {avpu}
Vital signs: {', '.join(vs_parts)}

[ED COURSE]
Initial nursing assessment completed at {patient['init_nurse_dt']}.
Patient evaluated for chief complaint of {cc}.

Procedures/Interventions:
- Intubation: {intubation}
- Ventilator: {ventilator}
- Vasopressor: {vasopressor}

[DIAGNOSIS]
Primary Diagnosis:
  {dx1} - {dx1_name}
"""

# 부 진단 추가
secondary_dx = []
if pd.notna(dx2_1):
    secondary_dx.append(f"  {dx2_1}")
if pd.notna(dx2_2):
    secondary_dx.append(f"  {dx2_2}")
if pd.notna(dx2_3):
    secondary_dx.append(f"  {dx2_3}")
if pd.notna(dx2_4):
    secondary_dx.append(f"  {dx2_4}")

if secondary_dx:
    note += "\nSecondary Diagnoses:\n"
    note += "\n".join(secondary_dx)

note += f"""

[DISPOSITION]
Discharge Time: {dc_dt}
ER Result Code: {patient['er_result']}

==================================================

Note: 본 Clinical Note는 snuh_20180103_base.xlsx의 환자 데이터를 기반으로 작성되었습니다.
"""

print(note)

# 파일로 저장
with open('Base_Clinical_Note.txt', 'w', encoding='utf-8') as f:
    f.write(note)

print("\n저장 완료: Base_Clinical_Note.txt")
