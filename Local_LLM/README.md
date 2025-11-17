Local LLM 비교 분석

개요
이 폴더는 OpenAI API (GPT-3.5-turbo)와 Local LLM (Llama 3.1 8B)을 사용한 Clinical Note 생성을 비교 분석합니다.
동일한 환자 데이터로 두 가지 방식의 성능, 비용, 품질을 체계적으로 비교하여 최적의 선택을 돕습니다.

분석 목표
- 목표 1: GPT-3.5-turbo vs Llama 3.1 8B 성능 비교
- 목표 2: 비용, 속도, 품질, 프라이버시 측면에서 장단점 분석
- 목표 3: Multi-Agent System에 적용 가능한 하이브리드 전략 제시

폴더 구조

```
Local_LLM/
├── README.md                          # 본 문서
├── LLM_Comparison_Analysis.ipynb      # 비교 분석 Jupyter Notebook
└── Admin_Agent_Local/                 # Llama 3.1 8B 버전
    ├── config/
    │   └── config.py                  # Ollama 설정
    ├── scripts/
    │   ├── data_extractor.py          # 데이터 추출 (기존과 동일)
    │   └── admin_agent_local.py       # Llama 3.1 8B 에이전트
    └── data/
        └── output_notes/              # Llama로 생성된 Clinical Note
```

Ollama 설치 및 설정

Ollama 설치

Windows:
1. https://ollama.com/download/windows 방문
2. 설치 파일 다운로드 및 실행
3. 설치 후 자동으로 서비스 시작됨

설치 확인
```bash
ollama --version
```

2. Llama 3.1 8B 다운로드

```bash
ollama pull llama3.1:8b
```

- 모델 크기: 약 4.7GB
- 소요 시간: 인터넷 속도에 따라 5-15분
- 필요 공간: 5GB 이상

3. Ollama 서버 실행

```bash
# 자동 실행되지만, 수동 실행이 필요한 경우:
ollama serve
```

- 기본 포트: `http://localhost:11434`
- 브라우저에서 접속하여 확인 가능

4. 모델 테스트

```bash
ollama run llama3.1:8b
```

대화형 인터페이스가 실행되며, 간단한 질문으로 모델을 테스트할 수 있습니다.

실행 방법

방법 1: Python 스크립트로 실행

```bash
Admin_Agent_Local 폴더로 이동
cd Local_LLM/Admin_Agent_Local/scripts

Llama 3.1 8B로 Clinical Note 생성
python admin_agent_local.py
```

*주의*: Ollama 서버가 실행 중이어야 함함

방법 2: Jupyter Notebook으로 분석

```bash
# Local_LLM 폴더에서
jupyter notebook LLM_Comparison_Analysis.ipynb
```

Notebook에서 단계별로 실행하며 결과를 확인할 수 있습니다.

비교 분석 항목

1. 정량적 비교
- 생성 시간: 환자당 평균 소요 시간
- 파일 크기: 생성된 Clinical Note의 크기 분포
- 비용 분석: 100명, 1000명 규모별 비용 계산

2. 정성적 비교
- 완전성: 모든 필수 섹션 포함 여부
- 정확성: 환자 데이터 반영의 정확도
- 자연스러움: 문장의 유창성
- 전문성: 의학 용어 사용의 적절성
- 일관성: 정보 간 모순 없음

3. 장단점 분석

| 항목 | GPT-3.5-turbo | Llama 3.1 8B |
|------|--------------|--------------|
| **품질** | 5 | 4 |
| **속도** | 4 | 3 |
| **비용** | 2 | 5 |
| **프라이버시** | 2 | 5 |
| **설정 편의성** | 5 | 3 |


GPT-3.5-turbo
- 프로토타입 개발
- 소규모 연구 (<100명)
- 최고 품질이 필요한 경우
- 빠른 결과가 필요한 경우
- 설정 간편함이 중요한 경우

Llama 3.1 8B 추천
- 대규모 연구 (>1000명)
- 민감한 환자 데이터 처리
- 오프라인 환경
- GPU 서버 보유
- Fine-tuning이 필요한 경우
- 장기적으로 많은 Clinical Note 생성

## 예상 결과

1) 비용 비교 (100명 기준)
- GPT-3.5-turbo: 약 $2-3
- Llama 3.1 8B: $0 (무료)

2) 속도 비교 (환자 1명)
- GPT-3.5-turbo: 5-10초
- Llama 3.1 8B (CPU): 20-60초
- Llama 3.1 8B (GPU): 10-20초

### 품질 비교
- GPT-3.5-turbo: 4.8/5.0
- Llama 3.1 8B: 4.0/5.0

## 하이브리드 전략

Multi-Agent System에서 각 Agent별로 다른 LLM 사용:

```
Formatter Agent → ED Physician Agent → Specialist Agent
       ↓                    ↓                  ↓
  Llama 3.1 8B       GPT-3.5-turbo          GPT-4
   (무료, 로컬)        (빠르고 품질)      (최고 품질)
```

장점:
- 비용 최적화: 간단한 작업은 로컬, 복잡한 작업은 API
- 프라이버시: 민감한 초기 데이터는 로컬 처리
- 품질: 중요한 의사결정은 고품질 모델 사용

## 하드웨어 요구사항

1) 최소 사양
- RAM: 8GB
- 저장 공간: 10GB
- CPU: Intel Core i5 이상 또는 동급

2) 권장 사양
- RAM: 16GB
- 저장 공간: 20GB
- CPU: Intel Core i7 이상
- GPU: NVIDIA GPU 4GB VRAM (선택, 10-20배 속도 향상)

제한사항

Llama 3.1 8B
1. 한글 성능: 영어보다 한글 성능이 낮을 수 있음
2. 하드웨어 의존: 좋은 하드웨어가 필요
3. 초기 설정: Ollama 설치 및 모델 다운로드 필요
4. 업데이트: 수동으로 모델 업데이트 필요

GPT-3.5-turbo
1. 비용: 사용량에 따른 과금
2. 프라이버시: 데이터가 외부 서버로 전송
3. 인터넷: 오프라인에서 사용 불가
4. 제한: Rate limit 및 할당량 존재

## 관련 문서

- `../Admin_Agent/README.md`: OpenAI API 버전
- `./Admin_Agent_Local/README.md`: Llama 3.1 8B 버전 (작성 예정)
- `./LLM_Comparison_Analysis.ipynb`: 상세 비교 분석

## 참고 자료

- [Ollama 공식 문서](https://ollama.com/docs)
- [Llama 3.1 모델 카드](https://ollama.com/library/llama3.1)
- [AutoGen with Local LLM](https://microsoft.github.io/autogen/docs/topics/non-openai-models/local-lmm)

---

작성일: 2025-11-16
작성자: Multi-Agent EME 프로젝트 팀
버전: 1.0
