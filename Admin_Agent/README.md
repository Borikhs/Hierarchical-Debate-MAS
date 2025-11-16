# Admin Agent - Clinical Note 자동 생성 시스템

## 📌 개요
Admin Agent는 SNUH 응급실 데이터를 입력받아 자동으로 Clinical Note(진료 기록)를 생성하는 AI 에이전트입니다.
AutoGen Framework를 사용하며, GPT-3.5-turbo 모델을 통해 환자 데이터를 의료진이 사용하는 표준 진료 기록 형식으로 변환합니다.
한글과 영어 두 가지 언어로 Clinical Note를 생성하여 국내외 의료 환경 모두에서 활용할 수 있습니다.

## 🎯 분석 목표
- 목표 1: SNUH 응급실 데이터(13개 파일)를 통합하여 초진 기록에 필요한 정보 추출
- 목표 2: AutoGen 단일 에이전트 구조로 AI 기반 Clinical Note 자동 생성 시스템 구축
- 목표 3: 한글/영어 이중 언어 Clinical Note 생성으로 다양한 의료 환경 지원
- 목표 4: Multi-Agent System의 Formatter Agent 개발을 위한 기반 구축

## 📋 분석 방법론

### "초진 기록(Primary Consultation)"의 정의
본 시스템에서 초진 기록은 다음과 같이 정의됩니다:

1. **시간적 기준**: 응급실 도착 시점부터 첫 평가 완료까지의 정보
2. **데이터 범위**: 9개 데이터 파일에서 추출한 초기 평가 정보
   - 기본정보, 진단명, 약품, 진료기록, 진단검사, 영상검사, 기능검사, 초기간호기록, 활력징후
3. **판단 기준**: 응급실 첫 진료 단계에서 의료진이 획득 가능한 정보
4. **제외 기준**: 초진 이후 시점의 정보 (타과의뢰, 퇴실간호기록, 간호일지 등)

#### 구체적 예시
- **포함**: 내원 당시 활력징후, 초기 혈액검사, 응급 투여 약물, 초기 진단명
- **제외**: 타과 의뢰서(초진 평가 후 발생), 입원 후 간호일지, 퇴실 시점 기록

### 사용한 데이터 파일 (9개)

| 번호 | 파일명 | 사용 이유 | 추출 정보 |
|-----|--------|----------|-----------|
| 1 | 기본정보 | 환자 식별 및 기본 인적사항 | 나이, 성별, 내원시각, 내원방법, ESI, 퇴실정보 |
| 2 | 진단명 | 주 진단 및 과거 병력 | 주 진단명, 부 진단명, 과거력 |
| 4 | 약품 | 응급실 투여 약물 | 응급 처치 약물 및 용량 |
| 5 | 진료기록 | 의료진 평가 기록 | 주 증상, 병력 청취 내용 |
| 7 | 진단검사 | 초기 혈액검사 결과 | Troponin, BNP, 전해질 등 |
| 8 | 영상검사 | 초기 영상 검사 결과 | X-ray, CT 등 |
| 9 | 기능검사 | 초기 기능 검사 결과 | 심전도(ECG) 등 |
| 10 | 초기간호기록 | 초기 간호 평가 | 신체 진찰, 환자 상태 |
| 13 | 활력징후 | 내원 시 활력징후 | 혈압, 맥박, 호흡, 체온, 산소포화도 |

### 제외된 데이터 파일 (4개)

| 번호 | 파일명 | 제외 이유 |
|-----|--------|-----------|
| 3 | 수혈+CP | 초진 단계에서는 일반적으로 수혈이 시행되지 않음. 수혈은 입원 후 처치에 해당 |
| 6 | 타과의뢰+의뢰서 | 초진 평가 완료 이후 단계에서 발생하는 정보 |
| 11 | 퇴실간호기록 | 퇴실 시점의 정보로 초진과 시간적으로 무관 |
| 12 | 간호일지 | 입원 이후의 경과 기록으로 초진 시점과 무관 |

## 🏗️ 시스템 구조

```
환자 데이터 입력
       ↓
[Data Extractor]  ← 9개 파일에서 데이터 추출 및 포맷팅
       ↓
[Admin Agent]     ← AutoGen AssistantAgent (GPT-3.5-turbo)
       ↓
Clinical Note 생성
       ↓
   ┌────┴────┐
한글 노트   영어 노트
```

## 📊 사용 데이터

### 입력 데이터
| 파일명 | 설명 | 위치 |
|--------|------|------|
| `201801-201803_1_기본정보.xlsx` | 환자 기본정보 (나이, 성별, 내원시각 등) | ../Data/ |
| `201801-201803_2_진단명.xlsx` | 진단명 정보 (주 진단 및 부진단) | ../Data/ |
| `201801-201803_4_약품.xlsx` | 투약 정보 (약품명, 투여량 등) | ../Data/ |
| `201801-201803_5_진료기록.xlsx` | 의료진 진료 기록 | ../Data/ |
| `201801-201803_7_진단검사.xlsx` | 혈액검사 등 진단검사 결과 | ../Data/ |
| `201801-201803_8_영상검사.xlsx` | X-ray, CT 등 영상검사 결과 | ../Data/ |
| `201801-201803_9_기능검사.xlsx` | 심전도 등 기능검사 결과 | ../Data/ |
| `201801-201803_10_초기간호기록.xlsx` | 초기 간호 평가 기록 | ../Data/ |
| `201801-201803_13_활력징후.xlsx` | 활력징후 (혈압, 맥박 등) | ../Data/ |
| `open-api key.txt` | OpenAI API 키 | ../ |

### 출력 데이터
| 파일 형식 | 설명 | 위치 |
|----------|------|------|
| `{환자ID}_korean_{timestamp}.txt` | 한글 Clinical Note | data/output_notes/ |
| `{환자ID}_english_{timestamp}.txt` | 영어 Clinical Note | data/output_notes/ |

## 🔧 주요 코드 설명

### 1. 설정 관리 (config/config.py)

#### 함수: get_api_key (config/config.py:9-32)

**목적**: OpenAI API key를 파일에서 읽어옵니다.

**수행 과정**:
1. 프로젝트 루트 경로 탐색 (줄 12-14)
2. `open-api key.txt` 파일 열기 (줄 18)
3. "sk-"로 시작하는 API key 추출 (줄 22-25)
4. API key 반환

**출력**: OpenAI API key 문자열

#### 초진 기록 파일 설정 (config/config.py:44-53)

9개 파일을 딕셔너리로 정의하여 초진 기록에 필요한 데이터만 선택적으로 로딩합니다.

```python
INITIAL_CONSULTATION_FILES = {
    "1_기본정보": "201801-201803_1_기본정보.xlsx",
    "2_진단명": "201801-201803_2_진단명.xlsx",
    ...
}
```

### 2. 데이터 추출 (scripts/data_extractor.py)

#### 클래스: PatientDataExtractor (data_extractor.py:17-299)

**목적**: 13개 데이터 파일에서 처음 2명의 환자 데이터를 추출하고 포맷팅합니다.

#### 메서드: load_basic_info (data_extractor.py:27-48)

**목적**: 기본정보 파일에서 처음 2명의 환자 ID를 추출합니다.

**수행 과정**:
1. 기본정보 엑셀 파일 읽기 (줄 32)
2. 처음 2행(2명) 추출 (줄 35)
3. 첫 번째 컬럼에서 환자 ID 추출 (줄 38)
4. 환자별 딕셔너리 초기화 (줄 41-44)

**출력**: 환자 ID 리스트 `[환자1_ID, 환자2_ID]`

#### 메서드: extract_patient_data (data_extractor.py:50-73)

**목적**: 각 환자에 대해 9개 파일에서 관련 데이터를 추출합니다.

**수행 과정**:
1. INITIAL_CONSULTATION_FILES의 각 파일 순회 (줄 55)
2. 엑셀 파일 읽기 (줄 60)
3. 환자 ID로 데이터 필터링 (줄 64)
4. 환자별 딕셔너리에 저장 (줄 66-70)

**입력**: 환자 ID 리스트
**출력**: 없음 (self.patient_data에 저장)

#### 메서드: format_for_clinical_note (data_extractor.py:89-113)

**목적**: 추출된 원본 데이터를 LLM이 이해하기 쉬운 형식으로 변환합니다.

**수행 과정**:
1. 기본정보에서 나이, 성별 등 추출 (줄 99-108)
2. 활력징후 포맷팅 (줄 109)
3. 진단명, 약품 등 각 항목 포맷팅 (줄 110-119)
4. 정리된 딕셔너리 반환 (줄 121)

**출력**: 포맷팅된 환자 데이터 딕셔너리

### 3. Admin Agent (scripts/admin_agent.py)

#### 클래스: AdminAgent (admin_agent.py:16-214)

**목적**: AutoGen을 사용하여 환자 데이터를 Clinical Note로 변환하는 AI 에이전트입니다.

#### 초기화 (admin_agent.py:24-108)

**목적**: AutoGen AssistantAgent를 한글용과 영어용 2개 생성합니다.

**수행 과정**:
1. API key 로딩 (줄 30)
2. LLM 설정 구성 (줄 33-38)
3. 한글 에이전트 생성 (줄 41-74)
   - System message에 한글 Clinical Note 형식 지정
   - Primary Consultation 구조 정의
4. 영어 에이전트 생성 (줄 77-104)
   - System message에 영어 Clinical Note 형식 지정

**중요 코드**:
```python
self.korean_agent = AssistantAgent(
    name="Korean_Clinical_Note_Writer",
    system_message="...",  # 한글 형식 지정
    llm_config=self.llm_config
)
```

#### 메서드: create_prompt_from_data (admin_agent.py:110-158)

**목적**: 환자 데이터를 LLM이 이해할 수 있는 프롬프트로 변환합니다.

**수행 과정**:
1. 환자 ID 및 기본정보 포맷팅 (줄 120-127)
2. 활력징후, 진단명 등 각 섹션 포맷팅 (줄 129-153)
3. 전체 프롬프트 문자열 생성 (줄 155)

**입력**: 포맷팅된 환자 데이터
**출력**: LLM 프롬프트 문자열

#### 메서드: generate_clinical_note (admin_agent.py:165-195)

**목적**: AutoGen을 통해 Clinical Note를 생성합니다.

**수행 과정**:
1. 프롬프트 생성 (줄 175)
2. 언어에 따라 적절한 에이전트 선택 (줄 178)
3. AutoGen의 generate_reply 호출 (줄 186-188)
4. 응답을 문자열로 변환하여 반환 (줄 190)

**핵심 로직** (admin_agent.py:186-188):
```python
response = agent.generate_reply(
    messages=[{"role": "user", "content": prompt}]
)
```

AutoGen의 AssistantAgent가 GPT-3.5-turbo를 통해 프롬프트를 처리하고 Clinical Note를 생성합니다.

**입력**:
- patient_data (dict): 포맷팅된 환자 데이터
- language (str): "korean" 또는 "english"

**출력**: 생성된 Clinical Note 문자열

#### 메서드: save_clinical_note (admin_agent.py:197-214)

**목적**: 생성된 Clinical Note를 파일로 저장합니다.

**수행 과정**:
1. 출력 폴더 생성 (줄 207)
2. 타임스탬프가 포함된 파일명 생성 (줄 210-211)
3. UTF-8 인코딩으로 파일 저장 (줄 214-215)

**출력 파일명 형식**: `{환자ID}_{언어}_{타임스탬프}.txt`

### 4. 메인 실행 함수 (admin_agent.py:217-260)

**목적**: 전체 프로세스를 순차적으로 실행합니다.

**실행 흐름**:
1. PatientDataExtractor로 2명의 환자 데이터 추출 (줄 226-227)
2. AdminAgent 초기화 (줄 232)
3. 각 환자에 대해:
   - 데이터 포맷팅 (줄 242)
   - 한글 Clinical Note 생성 및 저장 (줄 245-246)
   - 영어 Clinical Note 생성 및 저장 (줄 249-250)

## 🚀 실행 방법

### 필요한 도구
- Python 3.8 이상
- 필수 라이브러리:
  - `pandas`: 데이터 처리
  - `openpyxl`: 엑셀 파일 읽기
  - `pyautogen`: AutoGen Framework
  - `openai`: OpenAI API

### 설치

```bash
# Admin_Agent 폴더로 이동
cd Admin_Agent

# 필요한 라이브러리 설치
pip install pandas openpyxl pyautogen openai
```

### 실행 명령

```bash
# scripts 폴더로 이동
cd scripts

# Admin Agent 실행
python admin_agent.py
```

### 실행 결과

실행하면 다음과 같은 출력을 볼 수 있습니다:

```
============================================================
SNUH 응급실 환자 데이터 추출 시작
============================================================

📁 데이터 경로: ../Data
📋 사용할 파일 수: 9개
🚫 제외된 파일 수: 4개

제외된 파일 및 이유:
  - 3_수혈+CP: 초진 단계에서는 일반적으로 수혈이 시행되지 않음
  - 6_타과의뢰+의뢰서: 초진 평가 이후 단계에서 발생
  - 11_퇴실간호기록: 퇴실 시점의 정보로 초진과 무관
  - 12_간호일지: 입원 이후의 경과 기록으로 초진과 무관

✓ 기본정보 로딩 완료: 2명의 환자
✓ 2_진단명 로딩 완료
...

============================================================
Clinical Note 생성 중 (KOREAN)...
============================================================
✓ Clinical Note 생성 완료 (KOREAN)
✓ Clinical Note 저장 완료: R-1801-00000001_korean_20250115_143022.txt

============================================================
Clinical Note 생성 중 (ENGLISH)...
============================================================
✓ Clinical Note 생성 완료 (ENGLISH)
✓ Clinical Note 저장 완료: R-1801-00000001_english_20250115_143045.txt
```

## 📈 결과 해석

### 주요 발견사항

1. **데이터 통합 성공**: 9개 파일에서 초진에 필요한 정보를 성공적으로 추출하고 통합
2. **AI 기반 자동화**: GPT-3.5-turbo가 구조화된 데이터를 자연스러운 의료 기록으로 변환
3. **이중 언어 지원**: 동일한 환자 데이터로 한글/영어 Clinical Note 자동 생성
4. **표준화된 형식**: Primary Consultation 형식을 일관되게 유지

### 생성된 Clinical Note 구조

한글과 영어 모두 동일한 8개 섹션으로 구성됩니다:

1. **기본 정보(Basic Information)**: 나이, 성별, 내원 시각, 내원 방법
2. **임상 증상(Clinical Presentation)**: 주 증상, 활력징후, ESI 레벨
3. **신체 진찰(Physical Examination)**: 초기 신체 검진 소견
4. **관련 의학적 병력(Related Medical History)**: 과거력, 복용 약물, 알레르기
5. **초기 검사 결과(Initial Lab Results)**: 진단검사, 영상검사, 기능검사
6. **응급실 경과(ED Course)**: 투여된 약물 및 처치
7. **최종 진단(Diagnosis)**: 주 진단명 및 부 진단명
8. **배치(Disposition)**: 퇴실 정보 및 사유

### AutoGen Agent의 역할

- **입력**: 구조화된 환자 데이터 (딕셔너리 형태)
- **처리**: GPT-3.5-turbo를 통한 자연어 생성
- **출력**: 의료진이 작성한 것과 유사한 자연스러운 Clinical Note

## ⚠️ 분석의 제한점

### 1. 데이터 제한
- **샘플 크기**: 현재 처음 2명의 환자만 처리 (테스트 목적)
- **데이터 품질**: 원본 데이터의 결측값이나 오류가 Clinical Note에 영향
- **컬럼 의존성**: 엑셀 파일의 컬럼 순서 변경 시 오작동 가능

### 2. 방법론적 제한
- **AI 환각(Hallucination)**: GPT-3.5-turbo가 없는 정보를 추론하여 생성할 가능성
- **의학적 검증 부재**: 생성된 Clinical Note의 의학적 정확성을 검증하지 않음
- **단일 에이전트 한계**: 복잡한 의학적 판단이 필요한 경우 한계 존재
- **비용**: OpenAI API 사용으로 환자당 비용 발생

### 3. AutoGen 관련 제한
- **온라인 의존**: OpenAI API 호출을 위해 인터넷 연결 필수
- **응답 시간**: GPT-3.5-turbo의 응답 시간에 따라 처리 속도 변동
- **토큰 제한**: 매우 많은 데이터가 있는 환자의 경우 토큰 제한 초과 가능

### 4. 임상 활용 제한
- **연구 목적**: 이 시스템은 연구 및 개발 목적으로만 사용되어야 함
- **실제 진료 불가**: 생성된 Clinical Note를 실제 의료 기록으로 사용 불가
- **의료진 검토 필수**: 반드시 의료진의 검토와 승인이 필요

### 5. 확장성 제한
- **파일 경로 고정**: 데이터 파일 경로가 하드코딩되어 있어 유연성 부족
- **배치 처리 미지원**: 대량의 환자를 한 번에 처리하는 기능 없음
- **에러 복구**: 중간에 오류 발생 시 복구 메커니즘 없음

## 📝 향후 개선 방향

### 1. Multi-Agent 시스템으로 확장
현재는 단일 에이전트지만, 다음과 같은 Multi-Agent 구조로 발전 가능:

```
[Formatter Agent] → [ED Physician Agent] → [Specialist Agent]
        ↓                    ↓                      ↓
   데이터 정리        초기 평가 및 의뢰      전문과 의견
```

### 2. 의학적 검증 레이어 추가
```python
# 개선 예시: 검증 에이전트 추가
class MedicalValidator:
    def validate_clinical_note(self, note):
        # 의학적 모순 체크
        # 약물 상호작용 체크
        # 진단-증상 일치성 체크
        pass
```

### 3. 대량 처리 기능
```python
# 개선 예시: 배치 처리
def process_all_patients(data_path):
    extractor = PatientDataExtractor(data_path)
    all_patients = extractor.extract_all_patients()  # 모든 환자

    for patient in all_patients:
        generate_note(patient)
```

### 4. RAG(Retrieval-Augmented Generation) 통합
- MedRAG를 활용하여 의학 지식 기반 강화
- 최신 의학 가이드라인 참조

## ❓ 자주 묻는 질문

### Q1: 왜 처음 2명의 환자만 처리하나요?
**A**: 이 시스템은 프로토타입이며, Admin Agent의 작동 원리를 검증하기 위한 목적입니다. `data_extractor.py`의 `load_basic_info()` 메서드에서 `df.head(2)`를 `df.head(N)`으로 변경하면 N명의 환자를 처리할 수 있습니다.

### Q2: 왜 9개 파일만 사용하고 4개는 제외했나요?
**A**: 초진 기록은 응급실 **첫 평가 시점**의 정보만 포함해야 합니다. 타과의뢰(6번), 퇴실간호기록(11번), 간호일지(12번)는 초진 **이후** 시점의 정보이므로 제외했습니다. 수혈+CP(3번)는 초진 단계에서 거의 시행되지 않는 처치입니다.

### Q3: AutoGen의 단일 에이전트 구조란 무엇인가요?
**A**: AutoGen에서 단일 에이전트는 하나의 AssistantAgent만 사용하는 구조입니다. 복잡한 대화나 협업 없이, 입력(프롬프트) → 처리(LLM) → 출력(Clinical Note)의 직선적인 흐름을 따릅니다.

```python
# 단일 에이전트 구조
agent = AssistantAgent(...)
response = agent.generate_reply(messages=[...])
```

Multi-Agent 구조와 달리 여러 에이전트 간 대화나 역할 분담이 없습니다.

### Q4: GPT-3.5-turbo 대신 다른 모델을 사용할 수 있나요?
**A**: 네, 가능합니다. `config/config.py`의 `LLM_CONFIG`에서 모델을 변경할 수 있습니다:

```python
LLM_CONFIG = {
    "model": "gpt-4",  # 또는 "gpt-4-turbo"
    "temperature": 0.7,
    "max_tokens": 2000
}
```

단, GPT-4는 비용이 더 높지만 의학적 정확성이 향상될 수 있습니다.

### Q5: 생성된 Clinical Note를 실제 진료에 사용할 수 있나요?
**A**: **절대 불가능합니다**. 이 시스템은 연구 및 교육 목적으로만 사용되어야 합니다. 실제 의료 기록은:
- 의료진의 직접 작성과 검증 필수
- 법적 책임 문제
- 환자 안전에 직결

AI가 생성한 내용은 참고자료로만 활용하고, 반드시 의료진의 검토를 거쳐야 합니다.

### Q6: Multi-Agent System에서 어떻게 활용되나요?
**A**: Admin Agent는 Multi-Agent System의 **Formatter Agent**로 발전할 수 있습니다:

1. **현재 (Admin Agent)**: 원본 데이터 → Clinical Note
2. **발전 (Formatter Agent)**: 원본 데이터 → JSON 형태 Clinical Note → ED Physician Agent → Specialist Agent

Formatter Agent는 표준화된 JSON 형식으로 Clinical Note를 생성하여 다른 에이전트들에게 전달하는 역할을 합니다.

### Q7: 왜 한글과 영어 두 가지 언어로 생성하나요?
**A**:
- **국내 활용**: 한글 Clinical Note는 국내 의료진이 직접 사용
- **국제 연구**: 영어 Clinical Note는 국제 학술지 게재나 해외 연구진과 협업 시 사용
- **교육 목적**: 의학 용어의 한글-영어 대응 관계 학습에 활용

### Q8: API 키가 노출되면 어떻게 하나요?
**A**: `open-api key.txt` 파일은 `.gitignore`에 추가하여 버전 관리에서 제외해야 합니다. 만약 실수로 노출된 경우:
1. OpenAI 웹사이트에서 즉시 해당 키 삭제
2. 새로운 API 키 발급
3. `open-api key.txt` 파일 업데이트

## 🔗 관련 파일 및 문서

### 프로젝트 구조
```
Admin_Agent/
├── README.md                          # 본 문서
├── config/
│   └── config.py                      # 설정 파일
├── scripts/
│   ├── data_extractor.py              # 데이터 추출 모듈
│   └── admin_agent.py                 # Admin Agent 메인
└── data/
    └── output_notes/                  # 생성된 Clinical Note 저장
        ├── {환자ID}_korean_{timestamp}.txt
        └── {환자ID}_english_{timestamp}.txt
```

### 관련 문서
- `../CLAUDE.md`: 프로젝트 전체 가이드라인
- `../Primary Consultation(EX).txt`: Clinical Note 참고 형식
- `../ClinicalNotes/README.md`: Clinical Note 생성 관련 문서

### 참고 자료
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

## 📊 기술 스택

| 기술 | 버전 | 용도 |
|-----|------|------|
| Python | 3.8+ | 프로그래밍 언어 |
| AutoGen | Latest | Multi-Agent Framework |
| OpenAI API | GPT-3.5-turbo | LLM |
| pandas | Latest | 데이터 처리 |
| openpyxl | Latest | 엑셀 파일 읽기 |

---

**작성일**: 2025-01-15
**작성자**: Multi-Agent EME 프로젝트 팀
**버전**: 1.0
**최종 수정**: 2025-01-15
