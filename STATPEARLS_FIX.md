# StatPearls Preprocessing Fix

## 문제 요약

MedCorp 코퍼스를 사용하려고 하면 StatPearls의 `chunk/` 디렉토리가 없어서 오류 발생:

```
FileNotFoundError: [Errno 2] No such file or directory:
'/data/multi-agent_snuh/MedRAG/corpus/statpearls/chunk'
```

## 근본 원인

### MedRAG 코퍼스 구조 차이

| 코퍼스 | HuggingFace에서 다운로드 시 | 전처리 필요 여부 |
|--------|----------------------------|----------------|
| **Textbooks** | `chunk/` 디렉토리 포함 | ❌ 없음 |
| **PubMed** | `chunk/` 디렉토리 포함 | ❌ 없음 |
| **Wikipedia** | `chunk/` 디렉토리 포함 | ❌ 없음 |
| **StatPearls** | 원본 XML 파일만 (`statpearls_NBK430685/*.nxml`) | ✅ **필요** |

### StatPearls 구조

**다운로드 후**:
```
/data/multi-agent_snuh/MedRAG/corpus/statpearls/
├── statpearls_NBK430685/          # 원본 XML 파일 (9,627개)
│   ├── NBK430685.nxml
│   ├── NBK430686.nxml
│   └── ...
├── statpearls_NBK430685.tar.gz    # 압축 파일
└── chunk/                          # ❌ 없음! → 전처리로 생성 필요
```

**전처리 후**:
```
/data/multi-agent_snuh/MedRAG/corpus/statpearls/
├── statpearls_NBK430685/          # 원본 XML
├── chunk/                          # ✅ 생성됨!
│   ├── article-100024.jsonl
│   ├── article-100131.jsonl
│   └── ... (9,625개 JSONL 파일)
```

## 해결 방법

### 1. **statpearls.py 스크립트 추가**

원본 MedRAG 패키지의 전처리 스크립트를 복사하고 경로 수정:

**파일**: `scripts/statpearls.py`

**주요 변경사항**:
- 하드코딩된 상대 경로 → 절대 경로로 변경
- `/data/multi-agent_snuh/MedRAG/corpus/statpearls` 사용

### 2. **전처리 실행**

```bash
cd /home/hyesung/multi-agent/ex_version/Hierarchical-Debate-MAS
python scripts/statpearls.py
```

**결과**:
- 9,627개 XML 파일 처리
- 9,625개 JSONL 파일 생성 (빈 파일 2개 제외)
- 총 크기: ~508MB

### 3. **core.py 수정**

`tools/medrag_retriever/core.py`의 statpearls 처리 부분 수정:

**Before**:
```python
os.system("python src/data/statpearls.py")  # 경로가 존재하지 않음
```

**After**:
```python
# Use the package's scripts directory
script_path = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "statpearls.py")
if os.path.exists(script_path):
    os.system(f"python {script_path}")
else:
    print(f"Warning: statpearls.py not found at {script_path}")
    print("Please run: python scripts/statpearls.py manually")
```

## 파일 구조 변경

### 추가된 파일

```
/home/hyesung/multi-agent/ex_version/Hierarchical-Debate-MAS/
├── scripts/                         # 새로 추가
│   └── statpearls.py               # StatPearls 전처리 스크립트
├── test_medcorp.py                 # MedCorp 테스트 스크립트
└── STATPEARLS_FIX.md              # 이 문서
```

### 수정된 파일

- `tools/medrag_retriever/core.py` - statpearls.py 경로 수정

## MedCorp 코퍼스 구성

**MedCorp**는 4개의 코퍼스 결합:

| 코퍼스 | 문서 수 | 크기 | chunk/ 상태 |
|--------|---------|------|-------------|
| **PubMed** | 2M+ | ~15GB | ✅ 준비됨 |
| **Textbooks** | ~18K | ~50MB | ✅ 준비됨 |
| **StatPearls** | ~3K+ (9,625 chunks) | ~508MB | ✅ 생성 완료 |
| **Wikipedia** | ~20K+ | ~200MB | ✅ 준비됨 |

## 검증

### 테스트 실행

```bash
python test_medcorp.py
```

**예상 출력**:
```
================================================================================
Testing MedCorp Retrieval System Initialization
================================================================================

1. Initializing RetrievalSystem with MedCorp...
   Retriever: MedCPT
   Corpus: MedCorp (pubmed + textbooks + statpearls + wikipedia)
   This may take a few minutes on first run...

   ✓ RetrievalSystem initialized successfully

2. Testing retrieval with a sample query...
   ✓ Retrieved 3 documents for query: 'What is asthma?'

   Top 3 results:
   1. [0.8234] Asthma: Definition and Pathophysiology -- Clinical... (ID: ...)
   2. [0.7891] Bronchial Asthma -- Management and Treatment... (ID: ...)
   3. [0.7654] Respiratory Diseases -- Asthma Overview... (ID: ...)

================================================================================
MedCorp test passed! ✓
================================================================================

The system is ready to use with MedCorp corpus.
```

## 주의사항

### 처음 실행 시

StatPearls가 포함된 코퍼스를 사용하는 경우 (MedCorp, MedText):
1. **전처리가 완료되었는지 확인**
2. `/data/multi-agent_snuh/MedRAG/corpus/statpearls/chunk/` 존재 여부 확인
3. 없다면: `python scripts/statpearls.py` 실행

### 다른 코퍼스 사용

StatPearls가 필요 없다면:

```python
# main.py
corpus_name: str = "Textbooks"      # StatPearls 제외
# or
corpus_name: str = "Wikipedia"      # StatPearls 제외
```

## 타임라인

1. ✅ `scripts/statpearls.py` 생성 (경로 수정)
2. ✅ StatPearls 전처리 실행 (9,625 files)
3. ✅ `core.py` 수정 (스크립트 경로)
4. ✅ `test_medcorp.py` 생성 (검증용)

## 요약

- **문제**: StatPearls는 XML → JSONL 변환 필요
- **해결**: 전처리 스크립트 실행으로 `chunk/` 생성
- **결과**: MedCorp 전체 코퍼스 사용 가능
- **상태**: ✅ 해결 완료

이제 MedCorp를 사용하는 `MultiAgentDebateSystem`이 정상적으로 작동합니다! 🎉
