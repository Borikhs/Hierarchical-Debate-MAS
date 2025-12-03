# 베이스 이미지: python 3.x 슬림 버전
FROM python:3.10-slim

# 시스템 패키지 업데이트 & 필요한 dependency 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
RUN pip install --no-cache-dir pandas scikit-learn