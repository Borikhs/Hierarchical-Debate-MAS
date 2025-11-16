# -*- coding: utf-8 -*-
"""
AutoGen 테스트 스크립트
간단한 메시지로 AutoGen이 작동하는지 확인
"""

import sys
import os

# config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import get_api_key, LLM_CONFIG

print("="*60)
print("AutoGen 테스트 시작")
print("="*60)

# API key 로딩
try:
    api_key = get_api_key()
    print("[OK] API key 로딩 완료")
    print(f"API key: {api_key[:20]}...")
except Exception as e:
    print(f"[FAIL] API key 로딩 실패: {e}")
    sys.exit(1)

# AutoGen import 테스트
try:
    from autogen import AssistantAgent
    print("[OK] AutoGen import 성공")
except Exception as e:
    print(f"[FAIL] AutoGen import 실패: {e}")
    sys.exit(1)

# LLM 설정
llm_config = {
    "model": LLM_CONFIG["model"],
    "api_key": api_key,
    "temperature": 0.7
}

print(f"\nLLM 설정:")
print(f"  - Model: {llm_config['model']}")
print(f"  - Temperature: {llm_config['temperature']}")

# AssistantAgent 생성 테스트
try:
    agent = AssistantAgent(
        name="TestAgent",
        system_message="You are a helpful assistant. Please respond in Korean.",
        llm_config=llm_config
    )
    print("\n[OK] AssistantAgent 생성 성공")
except Exception as e:
    print(f"\n[FAIL] AssistantAgent 생성 실패: {e}")
    sys.exit(1)

# 간단한 메시지 생성 테스트
try:
    print("\n간단한 테스트 메시지 전송...")
    response = agent.generate_reply(
        messages=[{"role": "user", "content": "안녕하세요. 간단하게 자기소개 부탁합니다."}]
    )
    print(f"\n[OK] 응답 받음:")
    print(f"{response}")
except Exception as e:
    print(f"\n[FAIL] 메시지 생성 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("[OK] 모든 테스트 통과!")
print("="*60)
