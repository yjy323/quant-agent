#!/bin/bash

echo "📦 Streamlit 대시보드 실행 중..."
echo "📁 현재 디렉토리: $(pwd)"
# src 디렉토리를 PYTHONPATH에 추가
PYTHONPATH="$(pwd)/../src:$PYTHONPATH"
echo "📚 PYTHONPATH=$PYTHONPATH"

export PYTHONPATH
streamlit run app.py
