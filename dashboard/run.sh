#!/bin/bash

echo "📦 Streamlit 대시보드 실행 중..."
PROJECT_ROOT="/home/ubuntu/quant-agent"
cd "$PROJECT_ROOT/dashboard" || exit 1

# PYTHONPATH 설정 (예: src 디렉토리 활용 시)
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
echo "📚 PYTHONPATH=$PYTHONPATH"

# Streamlit 실행
nohup streamlit run app.py > ../logs/dashboard.log 2>&1 &
