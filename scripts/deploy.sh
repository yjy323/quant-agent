#!/bin/bash

set -e  # 에러 발생 시 즉시 종료
echo "🚀 배포 스크립트 실행 시작"

PROJECT_DIR="/home/ubuntu/quant-agent"
VENV_DIR="$PROJECT_DIR/.venv"
MAIN_PROCESS="main.py"
DASHBOARD_RUN_SCRIPT="$PROJECT_DIR/dashboard/run.sh"

echo "📦 가상환경 활성화 및 의존성 설치"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo "🧹 실행 중인 프로세스 종료"
pkill -f "$MAIN_PROCESS" || echo "ℹ️ main.py 프로세스 없음"
pkill -f streamlit || echo "ℹ️ streamlit 프로세스 없음"

echo "✅ 메인 프로그램 백그라운드 실행"
nohup python3 main.py > logs/main.log 2>&1 &

echo "✅ 대시보드 백그라운드 실행"
chmod +x "$DASHBOARD_RUN_SCRIPT"
nohup "$DASHBOARD_RUN_SCRIPT" > logs/dashboard.log 2>&1 &

echo "🎉 배포 완료!"
