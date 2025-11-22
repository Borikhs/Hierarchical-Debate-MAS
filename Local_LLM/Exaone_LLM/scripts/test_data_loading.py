# -*- coding: utf-8 -*-
"""
데이터 로딩 테스트 스크립트
"""

import sys
import os

# 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_extractor import PatientDataExtractor

print("\n" + "="*60)
print("데이터 로딩 테스트")
print("="*60)

# 데이터 경로
data_path = r"C:\Users\jojk6\SNUH_EME\Multi_Agent_EME\Local_LLM\Exaone_LLM\data\SNUH_Data"

# 데이터 추출기 초기화
extractor = PatientDataExtractor(data_path=data_path)

# 1명의 환자 데이터만 로드
print("\n[테스트] 1명의 환자 데이터 로딩...")
all_patient_data = extractor.extract_all(limit=1)

patient_ids = list(all_patient_data.keys())
print(f"\n[OK] 로드된 환자 ID: {patient_ids}")

# 첫 번째 환자 데이터 포맷팅
if patient_ids:
    patient_id = patient_ids[0]
    formatted_data = extractor.format_for_clinical_note(patient_id)

    print(f"\n[환자 {patient_id} 기본 정보]")
    for key, value in formatted_data['기본정보'].items():
        print(f"  - {key}: {value}")

    print(f"\n[OK] 데이터 로딩 및 포맷팅 테스트 성공!")
    print(f"  환자 ID: {patient_id}")
    print(f"  포맷팅된 데이터 키: {list(formatted_data.keys())}")
else:
    print("\n[ERROR] 환자 데이터를 찾을 수 없습니다.")

print("\n" + "="*60)
print("테스트 완료!")
print("="*60)
