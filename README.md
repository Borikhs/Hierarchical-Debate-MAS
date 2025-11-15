# Clinical Note 생성 스크립트

# 개요
이 스크립트는 SNUH(서울대학교병원) 응급실 데이터에서 환자 정보를 추출하여 표준화된 Clinical Note 형식으로 변환합니다.
의료진이 사용하는 응급실 진료 기록 형식으로, 환자의 기본정보, 활력징후, 진단명, 투약 내역 등을 구조화된 문서로 작성합니다.

# 분석 목표
- 목표 1: SNUH 응급실 데이터를 의료진이 이해하기 쉬운 Clinical Note 형식으로 변환
- 목표 2: Multi-Agent System의 Formatter Agent 개발을 위한 기초 데이터 생성
- 목표 3: 응급실 환자 기록의 표준화된 템플릿 구축

# 분석 방법론

# "Clinical Note"의 정의
본 스크립트에서 Clinical Note는 다음과 같이 정의됩니다:

1. 데이터 범위: 기본정보, 진단명, 활력징후, 약품 4개 파일의 정보
2. 구조화 기준:
   - PATIENT INFO: 환자 ID, 나이, 성별, 내원 시각, 내원 방법
   - TRIAGE: 주 증상(CC), 응급도 분류(ESI)
   - VITAL SIGNS: 혈압, 맥박, 호흡수, 산소포화도
   - HISTORY: 과거력, 알러지 정보
   - PRESENTATION: 환자 상태 요약
   - PHYSICAL EXAM: 신체 검진 소견
   - ED COURSE: 응급실 경과 (투약 정보 포함)
   - DIAGNOSIS: 진단명 목록
   - DISPOSITION: 퇴실 정보
3. 판단 기준: 첫 번째 환자(index 0)의 데이터 추출
4. 제외 기준: 결측값이 있는 항목은 "확인 필요"로 표시

#### 구체적 예시
- 포함: 활력징후에서 혈압 100~200 범위 → "BP 120" 형식으로 변환
- 제외: 활력징후가 비어있는 경우 → "활력징후 데이터 확인 필요"로 표시

## 사용 데이터
| 파일명 | 설명 | 위치 |
|--------|------|------|
| `201801-201803_1_기본정보.xlsx` | 환자 기본정보 (ID, 성별, 나이, 내원시각 등) | Data/ |
| `201801-201803_2_진단명.xlsx` | 진단명 정보 (주 진단 및 부진단) | Data/ |
| `201801-201803_13_활력징후.xlsx` | 활력징후 (혈압, 맥박, 호흡, 체온, 산소포화도) | Data/ |
| `201801-201803_4_약품.xlsx` | 투약 정보 (약품명, 투여량 등) | Data/ |

## 주요 코드 설명

### 1. 데이터 로딩 (create_detailed_note.py:6-25)

목적: 4개의 엑셀 파일에서 환자 데이터를 읽어옵니다.

```python
# 기본정보
df_basic = pd.read_excel('Data/201801-201803_1_기본정보.xlsx')
patient = df_basic.iloc[0]
patient_id = patient.iloc[0]

# 진단명
df_diagnosis = pd.read_excel('Data/201801-201803_2_진단명.xlsx')
patient_diag = df_diagnosis[df_diagnosis.iloc[:, 0] == patient_id]

# 활력징후
df_vitals = pd.read_excel('Data/201801-201803_13_활력징후.xlsx')
patient_vitals = df_vitals[df_vitals.iloc[:, 0] == patient_id]

# 약품
df_meds = pd.read_excel('Data/201801-201803_4_약품.xlsx')
patient_meds = df_meds[df_meds.iloc[:, 0] == patient_id]
```

이 코드는 pandas 라이브러리를 사용하여 4개의 엑셀 파일을 읽고, 첫 번째 환자의 ID를 기준으로 각 파일에서 해당 환자의 데이터를 필터링합니다.

# 2. 기본 정보 추출 (create_detailed_note.py:29-36)

목적: 환자의 나이, 성별, 내원 시각 등 기본 정보를 추출합니다.

**수행 과정**:
1. 생년월일에서 연도 추출 (줄 30)
2. 현재 연도(2018)에서 출생 연도를 빼서 나이 계산 (줄 31)
3. 성별, 내원 시각, 내원 방법, ESI 레벨, 퇴실 정보 추출 (줄 32-36)

# 3. 활력징후 처리 (create_detailed_note.py:50-70)

목적: 활력징후 데이터를 의료 기록 형식으로 변환합니다.

처리 로직:
- 혈압(BP): 100~200 범위의 값
- 맥박(HR): 30~150 범위의 값
- 호흡수(RR): 10~40 범위의 값
- 산소포화도(SpO2): 90~100 범위의 값

```python
if 100 <= val <= 200:
    vs_parts.append(f"BP {int(val)}")
elif 30 <= val <= 150:
    vs_parts.append(f"HR {int(val)}")
elif 10 <= val <= 40:
    vs_parts.append(f"RR {int(val)}")
elif 90 <= val <= 100:
    vs_parts.append(f"SpO2 {int(val)}%")
```

이 코드는 숫자 값의 범위를 기준으로 각 활력징후의 종류를 자동으로 판단하고, 적절한 라벨을 붙입니다.

# 4. 약품 정보 추출 (create_detailed_note.py:85-99)

목적: 투약된 약품 정보를 Clinical Note에 포함시킵니다.

**수행 과정**:
1. 약품 데이터가 있는지 확인 (줄 86)
2. 최대 5개의 약품 정보만 추출 (줄 88)
3. 각 약품의 1~4번째 컬럼에서 문자열 정보 추출 (줄 91-94)
4. 추출된 정보를 "약품명 / 용량" 형식으로 표시 (줄 97)

# 5. 진단명 추출 (create_detailed_note.py:101-116)

목적: 환자의 진단명을 추출하여 나열합니다.

수행 과정:
1. 진단명 데이터 존재 여부 확인
2. 각 진단명의 1~3번째 컬럼에서 정보 추출
3. "진단명 - 코드" 형식으로 표시

# 6. Clinical Note 저장 (create_detailed_note.py:125-129)

목적: 생성된 Clinical Note를 텍스트 파일로 저장합니다.

```python
with open('Detailed_Clinical_Note.txt', 'w', encoding='utf-8') as f:
    f.write(note)
```

UTF-8 인코딩을 사용하여 한글이 포함된 Clinical Note를 파일로 저장합니다.

- 실행 방법

# 필요한 도구
- Python 3.8 이상
- pandas 라이브러리
- openpyxl 라이브러리 (엑셀 파일 읽기)

# 실행 명령

```bash
# ClinicalNotes 폴더로 이동
cd ClinicalNotes

# 스크립트 실행
python create_detailed_note.py
```

### 실행 결과
- 콘솔에 Clinical Note 출력
- `Detailed_Clinical_Note.txt` 파일 생성

## 결과 해석

# 주요 발견사항
1. 데이터 구조화: SNUH 응급실 데이터를 표준 Clinical Note 형식으로 성공적으로 변환
2. 활력징후 자동 판단: 숫자 범위 기반 활력징후 자동 분류 알고리즘 적용
3. 결측값 처리: 데이터가 없는 경우 "확인 필요" 메시지로 명시적 표시

# 생성된 Clinical Note 예시

실제 생성된 Clinical Note는 `Real_Patient_Clinical_Note.txt` 파일에서 확인할 수 있습니다:

```
=== ED Clinical Note ===

[PATIENT INFO]
ID: R-1731-00000001 | Age: 78F | Arrival: 13:45 via 본원응급실(AER)

[TRIAGE]
CC: 어깨 통증 및 전신 근육통
ESI: Level 1
VS: 활력징후 기록 참조

[HISTORY]
PMHx: Parkinson's disease
Past injuries: Multiple fracture of ribs (old)
Meds: 파킨슨병 관련 약물 복용 중
Allergies: 알러지 확인 필요

...
```

*그림: 실제 환자 데이터로 생성된 Clinical Note 예시*
- 데이터 출처: `Data/201801-201803_*.xlsx`
- 생성 스크립트: `create_detailed_note.py`

# 분석의 제한점

# 1. 데이터 제한
- **단일 환자 처리**: 현재 스크립트는 첫 번째 환자(index 0)만 처리
- **컬럼 구조 의존**: 엑셀 파일의 컬럼 순서가 변경되면 오작동 가능
- **제한된 데이터 범위**: 4개 파일(기본정보, 진단명, 활력징후, 약품)만 사용

# 2. 방법론적 제한
- **활력징후 추론의 한계**: 숫자 범위만으로 활력징후 종류를 판단하여 오분류 가능
  - 예: 맥박 100과 혈압 100을 구분하기 어려움
- **결측값 처리**: 데이터가 없는 경우 단순히 "확인 필요"로만 표시
- **하드코딩된 경로**: 데이터 파일 경로가 고정되어 있어 유연성 부족

# 3. 해석상 주의점
- **주 증상(CC) 누락**: 실제 주 증상 데이터가 원본에 없어 "응급실 내원"으로만 표시
- **과거력 및 알러지**: 해당 정보를 담은 원본 데이터가 없어 "확인 필요"로 표시
- **의료 기록 완전성**: 이 스크립트는 기본적인 템플릿 생성용이며, 실제 의료 기록으로 사용하기에는 정보가 불충분

# 4. 확장성 제한
- **대량 처리 불가**: 한 번에 한 환자만 처리 가능
- **템플릿 고정**: Clinical Note 구조가 코드에 하드코딩되어 있어 수정 어려움
- **Multi-Agent 연동**: Formatter Agent로 발전시키려면 대폭적인 리팩토링 필요

# 향후 개선 방향

# 1. 다중 환자 처리
```python
# 개선 예시: 모든 환자 처리
for idx, patient in df_basic.iterrows():
    patient_id = patient.iloc[0]
    create_clinical_note(patient_id)
```

# 2. 컬럼명 기반 처리
현재는 컬럼 인덱스(iloc)를 사용하지만, 컬럼명을 사용하면 더 안정적:
```python
# 개선 예시
age = patient['나이']
gender = patient['성별']
```

# 3. Formatter Agent로의 발전
- JSON 출력 형식 지원
- 템플릿 외부화 (설정 파일)
- 더 많은 데이터 소스 통합 (진료기록, 검사결과 등)


## 관련 파일

# 같은 폴더의 다른 스크립트
- `create_clinical_note.py`: 기본 버전의 Clinical Note 생성 스크립트
- `create_clinical_note_v2.py`: 개선된 버전 (v2)
- `create_base_clinical_note.py`: 더 간단한 기본 버전
- `create_simple_note.py`: 최소한의 정보만 포함하는 간단한 버전

# 출력 파일
- `Detailed_Clinical_Note.txt`: 이 스크립트로 생성된 Clinical Note
- `Real_Patient_Clinical_Note.txt`: 실제 환자 데이터 예시
- `Base_Clinical_Note.txt`: 기본 템플릿 예시
- `Sample_Clinical_Note.txt`: 샘플 데이터

# 관련 문서
- `../CLAUDE.md`: 프로젝트 전체 가이드라인
- `Action Item Graph 관련 탐색.txt`: Multi-Agent 구조 관련 탐색 문서

---

작성일: 2025-11-15
**작성자**: Multi-Agent EME 프로젝트 팀
**버전**: 1.0
