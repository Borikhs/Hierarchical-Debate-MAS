# -*- coding: utf-8 -*-
"""
Admin Agent Configuration
OpenAI API key와 기타 설정을 관리하는 파일입니다.
"""

import os

def get_api_key():
    """
    OpenAI API key를 open-api key.txt 파일에서 읽어옵니다.

    Returns:
        str: OpenAI API key
    """
    # 프로젝트 루트 경로 찾기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # Admin_Agent
    project_root = os.path.dirname(project_root)  # Multi_Agent_EME

    api_key_file = os.path.join(project_root, 'open-api key.txt')

    try:
        with open(api_key_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # "open-api key: sk-..." 형식에서 key 부분만 추출
            if 'sk-' in content:
                api_key = content.split('sk-')[1]
                api_key = 'sk-' + api_key.strip()
                return api_key
            else:
                raise ValueError("API key 형식이 올바르지 않습니다.")
    except FileNotFoundError:
        raise FileNotFoundError(f"API key 파일을 찾을 수 없습니다: {api_key_file}")

# LLM 설정
LLM_CONFIG = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 2000
}

# 데이터 파일 경로
DATA_PATH = {
    "base": "../Data",
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
