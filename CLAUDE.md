📋 응급실 Decision Making Multi-Agent 프로젝트 가이드라인
🎯 핵심 원칙
이 문서는 응급실 Decision Making Multi-Agent 프로젝트의 모든 작업에 대한 가이드라인입니다. 모든 분석과 문서화는 프로그래밍 지식이 없는 사용자도 이해할 수 있도록 작성되어야 합니다.

📁 프로젝트 구조
1. 데이터 폴더 구조
Data/                  # 원본 데이터셋 
├── 201801-201803_1_기본정보                
├── 201801-201803_2_진단명               
├── 201801-201803_3_수혈+CP
├── 201801-201803_4_약품품
├── 201801-201803_5_진료기록록
├── 201801-201803_6_타과의뢰+의뢰서서
├── 201801-201803_7_진단검사
├── 201801-201803_8_영상검사
├── 201801-201803_9_기능검사사
├── 201801-201803_10_초기간호기록
├── 201801-201803_11_퇴실간호기록록
├── 201801-201803_12_간호일지지
├── 201801-201803_13_활력징후
├── snuh_20180103_base   # 내원 초기 정보
|
processed_data/           # 전처리된 데이터 저장 (분석 후 생성)
└── [전처리된 파일들이 저장될 위치]

중요 규칙:
Dataset/ 폴더의 데이터는 절대 수정하지 않습니다 (원본 보존)
모든 전처리된 데이터는 processed_data/ 폴더에 저장합니다
분석별 임시 데이터는 각 analysis_*/data/ 폴더에 저장합니다

2. 폴더 명명 규칙
모든 분석 폴더는 analysis_[주제명] 형식을 따릅니다
각 분석은 독립적인 폴더로 구성됩니다
예시: analysis_comprehensive, analysis_mortality, analysis_missing_values, analysis_samplingmethod

3. 각 분석 폴더의 표준 구조
analysis_[주제명]/
├── README.md                     # 분석 개요 및 빠른 시작 가이드
├── [주제]_analysis_report.ipynb     # 상세 분석 보고서
├── figures/                      # 시각화 결과
│   └── *.png/jpg                # 그래프 및 차트
├── scripts/                      # 실행 코드
│   ├── analysis/                # 분석 스크립트
│   │   └── *.py
│   └── preprocessing/           # 전처리 스크립트 (선택)
│       └── *.py
├── data/                        # 데이터 파일
│   ├── results.json            # 분석 결과
│   └── processed_*.csv         # 처리된 데이터
└── logs/                        # 실행 로그 (선택)
    └── analysis_log.txt

📝 문서 작성 규칙
1. 분석 정의 명시 규칙
모든 데이터 분석을 시작할 때는 반드시 분석의 핵심 개념을 명확히 정의해야 합니다.

필수 포함 사항
## 📋 분석 방법론

### "[분석 대상]"의 정의
본 분석에서 [분석 대상]은 다음과 같이 정의됩니다:

1. **시간적 기준**: [예: 입원일 기준 ±24시간]
2. **데이터 범위**: [예: 21개 주요 검사 항목]
3. **판단 기준**: [예: 최소 1개 이상 측정 시 "시행"으로 분류]
4. **제외 기준**: [예: 0세 환자, 재입원 등]

#### 구체적 예시
- 포함: [구체적인 포함 사례]
- 제외: [구체적인 제외 사례]

실제 예시
### "입원 당일 혈액검사 시행"의 정의
1. **시간적 기준**: admittime과 charttime이 같은 날짜 (00:00~23:59)
2. **데이터 범위**: 사전 정의된 21개 주요 혈액검사
3. **판단 기준**: 21개 중 최소 1개 이상 측정 시 "검사 시행"
4. **제외 기준**: 21개 외 다른 검사만 시행한 경우

예시:
- 포함: 입원일 오전 Sodium만 측정 → "검사 시행"
- 제외: 입원일 간기능검사만 시행 → "검사 미시행"
2. 파일 참조 형식
분석 스크립트 참조 규칙
모든 분석 스크립트는 문서에서 명확히 참조되어야 합니다:

스크립트 위치 명시: 정확한 파일 경로와 라인 번호 포함
분석 내용 설명: 해당 스크립트가 수행하는 분석 내용
생성된 결과물: 스크립트가 생성하는 그래프나 데이터 파일
## 데이터 분석 과정

### 1. 데이터 로딩 및 전처리
분석 스크립트: `scripts/analysis/data_preprocessing.py:1-50`
- 기능: MIMIC 데이터셋 로딩 및 기본 전처리
- 입력: `dataset2/core/admissions.csv`
- 출력: `data/processed_admissions.csv`

### 2. 통계 분석
분석 스크립트: `scripts/analysis/statistical_analysis.py:51-120`
- 기능: 기술통계 및 상관관계 분석
- 결과: `data/results.json`, `figures/correlation_matrix.png`
코드 참조

## 데이터 로딩 과정
`scripts/analysis/analyze_mimic_data.py:15-17` 에서 데이터를 불러옵니다.
이 부분은 pandas 라이브러리를 사용하여 CSV 파일을 읽는 과정입니다.
이미지 참조 - 필수 규칙
모든 생성된 이미지는 반드시 다음 형식으로 문서에 포함해야 합니다:

![입원 패턴 분석 결과](./figures/admission_patterns.png)
*그림 1: 시간대별 입원 환자 수 분포(예시)*
- 생성 스크립트: `scripts/analysis/admission_analysis.py:85-110`
- 데이터 출처: `dataset2/core/admissions.csv`
- 분석 기간: 2008-2019년
주의사항:

이미지가 생성되면 즉시 해당 문서에 위와 같은 형식으로 추가
이미지 경로는 상대 경로 사용 (./figures/...)
생성 스크립트 위치 반드시 명시
데이터 파일 참조

원본 데이터: `dataset2/core/admissions.csv`
- 환자의 입원 정보를 담고 있는 파일
- 총 523,740개의 입원 기록 포함

3. 분석 제한점 명시 규칙
모든 분석 문서에는 제한점 섹션을 필수로 포함해야 합니다.

## ⚠️ 분석의 제한점

### 1. 데이터 제한
- [데이터 범위, 샘플링 관련 제한]

### 2. 방법론적 제한
- [분석 방법의 한계, 가정 사항]

### 3. 해석상 주의점
- [결과 해석 시 고려사항]
4. 코드 설명 템플릿
### 함수: analyze_csv_file (scripts/analysis/analyze_mimic_data.py:4-39)

**목적**: CSV 파일을 읽고 기본적인 통계 분석을 수행합니다.

**입력 매개변수**:
- `filepath` (문자열): 분석할 파일의 경로
- `filename` (문자열): 파일 이름 (출력용)
- `nrows` (정수): 읽을 행의 개수 (기본값: 10000)

**수행 과정**:
1. 파일을 pandas DataFrame으로 읽기 (줄 9)
2. 데이터 크기와 컬럼 정보 출력 (줄 11-14)
3. 데이터 타입 확인 (줄 16-17)
4. 기본 통계 계산 (줄 22-23)
5. 결측값 분석 (줄 25-32)

**출력**: 분석된 DataFrame 객체
📦 패키지 관리자 - uv 사용
이 프로젝트는 uv를 사용하여 Python 패키지를 관리합니다.

Python 스크립트 실행 방법
# 가상환경 활성화 (프로젝트 루트에서)
source .venv/bin/activate

# 스크립트 실행
python [스크립트 경로]
중요: 모든 Python 스크립트는 반드시 uv 가상환경을 활성화한 후 실행해야 합니다.

📊 샘플링 방법론
균형잡힌 데이터셋 구축 (analysis_samplingmethod)
MIMIC-IV의 대규모 데이터(523,740건)에서 사망률 예측 연구를 위한 균형잡힌 1,200건 샘플을 추출하는 방법론입니다.

샘플링 전략
그룹	정의	샘플 수	비율
병원 내 사망	hospital_expire_flag = 1	300	25%
병원 후 사망	hospital_expire_flag = 0 & dod is not null	300	25%
생존	dod is null	600	50%

주요 특징
재현가능성: random_state=42 사용으로 동일한 샘플 재현 가능
균형 데이터: 원본 사망률 2.5%의 불균형 문제 해결
제외 기준: 0세 환자 제외 (신생아의 특수한 생리학적 특성)
샘플 데이터 위치
processed_data/
├── core/
│   ├── admissions_sampled.csv   # 1,200건 입원 정보
│   ├── patients_sampled.csv     # 1,171명 환자 정보
│   └── transfers_sampled.csv    # 4,682건 병동 이동

활용 예시
# 샘플링 실행
cd analysis_samplingmethod
python scripts/analysis/perform_sampling_test.py

# 검증 실행
cd ..
python validate_sampling.py
참고: 이 샘플링은 머신러닝 모델 학습용으로, 실제 사망률 통계 분석에는 전체 데이터를 사용해야 합니다.

📁 특별 폴더 구조: analysis_prediction
예측 모델 개발을 위한 analysis_prediction 폴더는 다른 분석 폴더와 달리 특별한 구조를 따릅니다:

analysis_prediction/
├── README.md                    # 전체 개요
├── docs/                        # 📚 모든 문서
│   ├── guides/                  # 가이드 문서
│   │   ├── Modeling_Guide.md
│   │   └── MIMIC_IV_Age_Calculation_Guide.md
│   └── datasets/                # 데이터셋 분석 문서
│       ├── Essential_Dataset_Analysis.md
│       ├── Extended_Dataset_Analysis.md
│       └── Comprehensive_Dataset_Analysis.md
├── data/                        # 📊 데이터 파일
│   ├── raw/                     # 원본 통합 데이터
│   ├── essential/               # Essential 데이터셋 (결측률 6%)
│   ├── extended/                # Extended 데이터셋 (결측률 22%)
│   └── comprehensive/           # Comprehensive 데이터셋 (결측률 37%)
├── models/                      # 🤖 모델 개발 (각 데이터셋별)
│   ├── essential/
│   │   ├── notebooks/          # Jupyter notebooks
│   │   ├── scripts/            # Python 스크립트
│   │   └── results/            # 모델 결과
│   ├── extended/
│   └── comprehensive/
├── scripts/                     # 🔧 유틸리티 스크립트
│   └── data_preparation/        # 데이터 준비 스크립트
├── figures/                     # 📈 시각화
└── results/                     # 📋 최종 결과

특징
3개 레벨 데이터셋: Essential (기본), Extended (확장), Comprehensive (포괄)
각 데이터셋별 독립 모델링: models/ 폴더 아래 분리
체계적 문서화: docs/ 폴더에 가이드와 분석 문서 분리
재현가능한 실험: notebooks와 scripts 분리

🚀 새 분석 추가 가이드
분석 시작 전 체크리스트
 분석 대상의 명확한 정의 작성
 포함/제외 기준 명시
 예상되는 제한점 파악
 필요한 데이터 파일 확인

1단계: 폴더 구조 생성
mkdir -p analysis_[새분석주제]/{figures,scripts/analysis,data}
# 또는 개별적으로:
mkdir analysis_[새분석주제]
mkdir analysis_[새분석주제]/figures
mkdir -p analysis_[새분석주제]/scripts/analysis
mkdir analysis_[새분석주제]/data
2단계: 필수 파일 및 폴더 생성
README.md: 아래 템플릿 사용

[주제]_analysis_report.ipynb: 상세 분석 보고서(주피터 파일로 작성)
scripts/analysis/: 분석 스크립트 폴더
data/: 결과 데이터 폴더
figures/: 시각화 저장 폴더

3단계: README.md 템플릿
# [분석 제목]

## 📌 개요
이 분석의 목적과 중요성을 2-3문장으로 설명합니다.
비전문가도 이해할 수 있는 용어를 사용합니다.

## 🎯 분석 목표
- 목표 1: 구체적인 분석 목표
- 목표 2: 기대되는 결과
- 목표 3: 실제 적용 방안

## 📋 분석 방법론

### "[핵심 분석 대상]"의 정의
본 분석에서 [분석 대상]은 다음과 같이 정의됩니다:

1. **시간적 기준**: [명확한 시간 범위]
2. **데이터 범위**: [포함되는 데이터 항목]
3. **판단 기준**: [분류/판단 기준]
4. **제외 기준**: [제외되는 경우]

#### 구체적 예시
- 포함: [실제 포함 사례]
- 제외: [실제 제외 사례]

## 📊 사용 데이터
| 파일명 | 설명 | 크기 |
|--------|------|------|
| `../dataset2/core/admissions.csv` | 입원 정보 | 523,740 행 |
| `../dataset2/core/patients.csv` | 환자 기본정보 | 382,278 행 |

## 🔧 주요 코드 설명

### 데이터 로딩 (scripts/analysis/[스크립트명].py:15-20)
```python
# 간단한 코드 예시
df = pd.read_csv('파일경로')
이 코드는 CSV 파일을 읽어 데이터프레임으로 변환합니다.

🚀 실행 방법
필요한 도구
Python 3.8 이상
pandas, numpy 라이브러리
실행 명령
cd analysis_[분석주제]
python [스크립트명].py
📈 결과 해석
주요 발견사항
발견 1: 구체적인 수치와 함께 설명
발견 2: 시각화 자료 참조
발견 3: 실무 적용 가능성
시각화 결과
결과 그래프 그림 설명: 무엇을 보여주는지 자세히 설명

⚠️ 분석의 제한점
1. 데이터 제한
[샘플링 방법, 데이터 범위 등]
2. 방법론적 제한
[분석 방법의 한계, 가정 사항]
3. 해석상 주의점
[결과를 해석할 때 주의할 점]
❓ 자주 묻는 질문
Q: 이 분석은 왜 중요한가요? A: [답변]

Q: 결과를 어떻게 활용할 수 있나요? A: [답변]

🔗 관련 분석
종합 분석
샘플링 방법론
결측값 분석

---

## 🎨 시각화 가이드라인

### 1. 한글 깨짐 방지 설정

모든 그래프 생성 스크립트에는 **반드시 한글 폰트 설정**을 포함해야 합니다.

```python
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# 운영체제별 한글 폰트 설정
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = 'AppleGothic'
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:  # Linux
    # Linux의 경우 나눔폰트 설치 필요: apt-get install fonts-nanum
    plt.rcParams['font.family'] = 'NanumGothic'

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False
2. 그래프 저장 규칙
모든 그래프는 figures/ 폴더에 저장
파일명은 내용을 설명하는 영문 사용
예: mortality_by_age.png, admission_trends.png
3. 그래프 문서화 규칙
필수 참조 형식
모든 생성된 그래프는 반드시 markdown 이미지 문법으로 문서에 포함되어야 합니다:

![그래프 제목](./figures/파일명.png)
*그림 번호: 그래프가 보여주는 내용을 상세히 설명*
- X축: 무엇을 나타내는지
- Y축: 무엇을 나타내는지
- 주요 패턴: 발견된 중요한 패턴
- 생성 스크립트: `scripts/analysis/스크립트명.py:라인번호`
실제 예시
![입원 환자 연령 분포](./figures/age_distribution.png)
*그림 1: MIMIC-IV 데이터셋의 입원 환자 연령 분포*
- X축: 연령대 (10세 단위)
- Y축: 환자 수
- 주요 패턴: 60-70대에서 가장 높은 입원율
- 생성 스크립트: `scripts/analysis/age_analysis.py:45-67`

🔍 Multi-Agent관련 공지사항
- Framework: AutoGen 사용
- Agent 완성 후, 관련 설명 파일을 script/ 에 저장(에이전트이름_analysis.ipynb와 같은 형식으로 저장)
- 설명파일에 들어갈 내용은, 에이전트의 구조 및 원리, 역할, 순서/흐름, 코드 분석 등을 작성
- Autogen의, 다양한 Tool들을 정의하여 작성(각각의 설명도 필요)

🔍 Multi-Agent 구성
- Formatter Agent: 전처리된 Data에서 환자 데이터를 Clinical Note의 형식으로 변환하여 Output으로 내놓는다.(Rule-based model with predefined normal ranges and formats)
* Clinical Notes 예시
"13-year-old male walks into the ED with his mother on a Friday night. Mom states, 'I didn't realize he was out of his medications for his ADHD, and I don't want him to miss a day.' The patient is cooperative and pleasant. VS: BP 108/72, HR 78, RR 14, T 98.6°F."

- ED physician: Decides whether consultation is needed and to whom. Drafts consultation note.

- Specialist: MedRAG활용하여, 의료 전문가 Agent의 역할을 수행(과별로 Agent 분류 예정)
1) 



- 전처리된 Data에서 다시 Formatter Agent를 통해, Clinical Note를 정해진 양식대로 변환한다.
- Formatter Agent는 Clinical Note의 형식(json) 형태로 Ouput하여 해당 양식을 후에 Specialist Agent나, ED Physician Agent에게 넘긴다.

🔍 Multi-Agent 모델 생성 관련
- Data(원본데이터) 중에서 필요한 부분을 Processed하여서, 전치리된 Data를 사용한다.
- 전처리된 Data에서 다시 Formatter Agent를 통해, Clinical Note를 정해진 양식대로 변환한다.
- Formatter Agent는 Clinical Note의 형식(json) 형태로 Ouput하여 해당 양식을 후에 Specialist Agent나, ED Physician Agent에게 넘긴다.

🔍 코드 품질 체크리스트
분석 스크립트 작성 시
 모든 함수에 docstring 추가
 중요한 코드 블록에 주석 추가
 변수명은 의미를 알 수 있게 작성
 결과는 JSON 또는 CSV로 저장
 에러 처리 코드 포함

문서 작성 시
 코드 위치 참조 (파일명:줄번호)
 모든 이미지에 설명 추가
 비전문가도 이해 가능한 용어 사용
 실행 방법 단계별 설명
 FAQ 섹션 포함

📚 용어 설명
의료 용어
MIMIC: Medical Information Mart for Intensive Care (중환자 의료정보 데이터베이스)
ICU: Intensive Care Unit (중환자실)
LOS: Length of Stay (재원 기간)
Admission: 입원
Discharge: 퇴원
Transfer: 병동 이동
데이터 분석 용어
DataFrame: 표 형태의 데이터 구조
CSV: Comma-Separated Values (쉼표로 구분된 데이터 파일)
JSON: JavaScript Object Notation (구조화된 데이터 형식)
Null/Missing Value: 결측값 (비어있는 데이터)

💡 초보자를 위한 팁
Python 코드 읽기
#으로 시작하는 줄은 주석(설명)입니다
import는 필요한 도구를 가져오는 명령입니다
def는 함수(기능)를 정의하는 키워드입니다
들여쓰기는 코드의 구조를 나타냅니다
데이터 분석 이해하기
데이터 로딩: 파일을 프로그램으로 읽어오기
전처리: 분석에 적합하게 데이터 정리
분석: 통계 계산이나 패턴 찾기
시각화: 그래프로 결과 표현
해석: 결과의 의미 설명

🔄 업데이트 이력
날짜	버전	변경사항
2025-08-12	1.0	초기 가이드라인 작성
2025-08-18	1.1	analysis_basic 제거, 전체 데이터 분석 기준으로 업데이트
2025-08-18	1.2	샘플링 방법론 섹션 추가 (analysis_samplingmethod)
2025-08-19	1.3	분석 정의 명시 규칙 및 제한점 섹션 필수화
2025-08-20	1.4	한글 깨짐 방지 코드, 스크립트 참조 규칙, 이미지 참조 규칙 추가
📮 문의사항
프로젝트 관련 문의사항이 있으시면 이슈를 생성하거나 README.md를 참조해주세요.