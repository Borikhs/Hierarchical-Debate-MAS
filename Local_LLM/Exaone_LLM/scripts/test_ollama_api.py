# -*- coding: utf-8 -*-
"""
Ollama API 연결 테스트
"""

import requests

print("\n" + "="*60)
print("Ollama API 연결 테스트")
print("="*60)

base_url = "http://localhost:11434"

# 1. 서버 상태 확인
print("\n[1] Ollama 서버 상태 확인...")
try:
    response = requests.get(f"{base_url}/api/tags", timeout=5)
    if response.status_code == 200:
        print(f"  [OK] Ollama 서버 정상 작동")
        models = response.json().get("models", [])
        print(f"  설치된 모델 수: {len(models)}")
        for model in models:
            print(f"    - {model['name']}")
    else:
        print(f"  [FAIL] 서버 응답 오류: {response.status_code}")
except Exception as e:
    print(f"  [FAIL] 연결 실패: {e}")
    exit(1)

# 2. 간단한 생성 테스트
print("\n[2] Exaone 모델 생성 테스트...")
print("  프롬프트: '안녕하세요'")

payload = {
    "model": "exaone3.5:7.8b",
    "prompt": "안녕하세요. 짧게 인사해주세요.",
    "stream": False,
    "options": {
        "temperature": 0.7,
        "num_predict": 50
    }
}

try:
    response = requests.post(f"{base_url}/api/generate", json=payload, timeout=30)
    if response.status_code == 200:
        result = response.json()
        generated_text = result.get("response", "")
        print(f"  [OK] 생성 성공!")
        print(f"  응답: {generated_text[:100]}...")
    else:
        print(f"  [FAIL] 생성 실패: {response.status_code}")
except Exception as e:
    print(f"  [FAIL] 오류 발생: {e}")

print("\n" + "="*60)
print("테스트 완료!")
print("="*60)
