# -*- coding: utf-8 -*-
"""
Admin Agent Local Configuration
Llama 3.1 8B 모델을 Ollama를 통해 로컬에서 실행하는 설정 파일입니다.
"""

import os

# Llama 3.1 8B 설정 (Ollama)
LLM_CONFIG = {
    "model": "llama3.1:8b",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",  # Ollama는 API key가 필요 없지만 AutoGen에서 요구하므로 더미 값
    "temperature": 0.7,
    "max_tokens": 2000
}

# 데이터 파일 경로
DATA_PATH = {
    "base": "../../Data",
    "output": "./data/output_notes"
}

# 초진 기록에 사용할 데이터 파일 목록
# 초진 기록 관점에서 선택된 파일들
INITIAL_CONSULTATION_FILES = {
    "1_기본정보": "201801-201803_1_기본정보.xlsx",
    "2_진단명": "201801-201803_2_진단명.xlsx",
    "4_약품": "201801-201803_4_약품.xlsx",
    "5_진료기록": "201801-201803_5_진료기록.xlsx",
    "7_진단검사": "201801-201803_7_진단검사.xlsx",
    "8_영상검사": "201801-201803_8_영상검사.xlsx",
    "9_기능검사": "201801-201803_9_기능검사.xlsx",
    "10_초기간호기록": "201801-201803_10_초기간호기록.xlsx",
    "13_활력징후": "201801-201803_13_활력징후.xlsx"
}

# 제외된 파일 및 이유
EXCLUDED_FILES = {
    "3_수혈+CP": "초진 단계에서는 일반적으로 수혈이 시행되지 않음",
    "6_타과의뢰+의뢰서": "초진 평가 이후 단계에서 발생",
    "11_퇴실간호기록": "퇴실 시점의 정보로 초진과 무관",
    "12_간호일지": "입원 이후의 경과 기록으로 초진과 무관"
}

# Ollama 설치 및 실행 가이드
OLLAMA_GUIDE = """
=== Ollama 설치 및 Llama 3.1 8B 실행 가이드 ===

1. Ollama 설치:
   - Windows: https://ollama.com/download/windows
   - 설치 후 자동으로 서비스 실행됨

2. Llama 3.1 8B 모델 다운로드:
   ollama pull llama3.1:8b

3. Ollama 서버 실행 확인:
   - 기본적으로 http://localhost:11434 에서 실행
   - 브라우저에서 http://localhost:11434 접속하여 확인

4. 모델 테스트:
   ollama run llama3.1:8b

=== 참고 사항 ===
- Llama 3.1 8B 모델 크기: 약 4.7GB
- 필요 메모리: 최소 8GB RAM 권장
- GPU 가속: NVIDIA GPU 있으면 자동 활용
"""
