# 🚀 Ollama 설치 가이드 (Windows)

## 📥 1단계: Ollama 다운로드

### 자동 다운로드 (PowerShell)
```powershell
# PowerShell에서 실행
Start-Process "https://ollama.com/download/windows"
```

### 수동 다운로드
1. 브라우저에서 https://ollama.com/download/windows 접속
2. **OllamaSetup.exe** 다운로드
3. 다운로드한 파일 실행

---

## 🔧 2단계: Ollama 설치

1. **OllamaSetup.exe** 더블클릭
2. 설치 마법사 진행 (Next → Next → Install)
3. 설치 완료 후 **Ollama 서비스 자동 시작**
4. 시스템 트레이에 Ollama 아이콘 확인

---

## ✅ 3단계: 설치 확인

### 명령 프롬프트에서 확인
```bash
ollama --version
```

**예상 출력:**
```
ollama version 0.x.x
```

### Ollama 서버 확인
```bash
# 브라우저에서 접속
http://localhost:11434
```

**예상 출력:**
```
Ollama is running
```

---

## 📦 4단계: Llama 3.1 8B 다운로드

```bash
ollama pull llama3.1:8b
```

**진행 상황:**
```
pulling manifest
pulling 8934d96d3f08... 100%
pulling 8c17c2ebb0ea... 100%
pulling 7c23fb36d801... 100%
pulling 2e0493f67d0c... 100%
pulling fa304d675061... 100%
pulling 42ba7f8a01dd... 100%
verifying sha256 digest
writing manifest
success
```

- **소요 시간**: 5-15분 (인터넷 속도에 따라)
- **다운로드 크기**: 약 4.7GB

---

## 🧪 5단계: 모델 테스트

```bash
ollama run llama3.1:8b
```

**대화형 인터페이스 실행:**
```
>>> 안녕하세요
안녕하세요! 무엇을 도와드릴까요?

>>> /bye
```

---

## 🎯 6단계: Admin Agent Local 실행 준비 완료!

설치가 완료되면 다음 명령으로 실행할 수 있습니다:

```bash
cd Local_LLM/Admin_Agent_Local/scripts
python admin_agent_local.py
```

---

## ⚙️ 문제 해결

### Ollama 서비스가 시작되지 않는 경우

**방법 1: 수동으로 서비스 시작**
```bash
ollama serve
```

**방법 2: Windows 서비스 확인**
1. `Win + R` → `services.msc` 입력
2. "Ollama" 서비스 찾기
3. 우클릭 → 시작

### 모델 다운로드 실패

**인터넷 연결 확인:**
```bash
ping ollama.com
```

**디스크 공간 확인:**
- 최소 10GB 이상의 여유 공간 필요

### "ollama: command not found" 오류

**환경 변수 확인:**
1. `Win + R` → `sysdm.cpl` 입력
2. 고급 → 환경 변수
3. Path에 Ollama 경로 추가:
   - `C:\Users\[사용자명]\AppData\Local\Programs\Ollama`

---

## 📊 시스템 요구사항

### 최소 사양
- **OS**: Windows 10/11
- **RAM**: 8GB
- **디스크**: 10GB 여유 공간
- **CPU**: Intel Core i5 또는 AMD Ryzen 5 이상

### 권장 사양
- **RAM**: 16GB 이상
- **디스크**: 20GB 여유 공간
- **GPU**: NVIDIA GPU (선택, 10-20배 속도 향상)
  - CUDA 지원 GPU
  - 4GB VRAM 이상

---

## 🚀 빠른 시작 체크리스트

- [ ] Ollama 다운로드
- [ ] Ollama 설치
- [ ] `ollama --version` 확인
- [ ] `ollama pull llama3.1:8b` 실행
- [ ] `ollama list` 로 모델 확인
- [ ] `ollama run llama3.1:8b` 테스트
- [ ] Admin Agent Local 실행 준비 완료!

---

## 📚 추가 자료

- [Ollama 공식 문서](https://github.com/ollama/ollama/blob/main/README.md)
- [Llama 3.1 모델 카드](https://ollama.com/library/llama3.1)
- [Windows 설치 가이드](https://github.com/ollama/ollama/blob/main/docs/windows.md)

---

**다음 단계**: 설치가 완료되면 `check_ollama.py`를 실행하여 설치 상태를 확인하세요!

```bash
python Local_LLM/check_ollama.py
```
