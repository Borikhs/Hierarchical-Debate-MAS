# -*- coding: utf-8 -*-
import pandas as pd

# 기본정보만 읽기
df_basic = pd.read_excel('Data/201801-201803_1_기본정보.xlsx')
patient = df_basic.iloc[0]

# 환자 ID
patient_id = patient.iloc[0]

# 나이 계산
birth_year = int(str(patient.iloc[3])[:4])
age = 2018 - birth_year

# 성별
gender = patient.iloc[2]

# 도착 시간
arrival_time = str(patient.iloc[8]).split()[1][:5] if ' ' in str(patient.iloc[8]) else '13:45'

# 도착 방법
arrival_method = patient.iloc[7]

# ESI 레벨
esi_level = patient.iloc[4]

# 최종 결과
disposition = patient.iloc[10]

# Clinical Note 작성
note = f"""=== ED Clinical Note ===

[PATIENT INFO]
ID: {patient_id} | Age: {age}{gender} | Arrival: {arrival_time} via {arrival_method}

[TRIAGE]
CC: 응급실 내원
ESI: Level {esi_level}
VS: 활력징후 데이터 확인 필요

[HISTORY]
PMHx: 과거력 확인 필요
Allergies: 알러지 확인 필요

[PRESENTATION]
{age}yo {gender} presents to ED via {arrival_method}.

[PHYSICAL EXAM]
Gen: 초기 평가 참조
Vital signs documented at triage

[ED COURSE]
Labs: 진단검사 진행
Imaging: 영상검사 진행
Rx: 투여약물 기록 참조

[DIAGNOSIS]
진단명 확인 필요

[DISPOSITION]
→ {disposition}

==================================================
"""

print(note)

# 파일로 저장
with open('Sample_Clinical_Note.txt', 'w', encoding='utf-8') as f:
    f.write(note)

print("\n저장 완료: Sample_Clinical_Note.txt")
