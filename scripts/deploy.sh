#!/bin/bash

set -e  # 에러 발생 시 즉시 종료

PROJECT_DIR="/home/ubuntu/quant-agent"
VENV_DIR="$PROJECT_DIR/.venv"
MAIN_PROCESS="main.py"
DASHBOARD_RUN_SCRIPT="$PROJECT_DIR/dashboard/run.sh"

echo "🚀 [1] 프로젝트 디렉토리 이동: $PROJECT_DIR"
cd "$PROJECT_DIR" || exit 1

echo "📥 [2] Git 최신 코드 pull"
git reset --hard
git pull origin main

echo "📦 [3] 가상환경 활성화 및 의존성 설치"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo "🧹 [4] 백그라운드 실행 중인 기존 프로세스 종료"
pkill -f "$MAIN_PROCESS" || true
pkill -f streamlit || true

echo "✅ [5] 메인 프로그램 백그라운드 실행"
nohup python3 main.py > logs/main.log 2>&1 &

echo "✅ [6] 대시보드 실행"
chmod +x "$DASHBOARD_RUN_SCRIPT"
nohup "$DASHBOARD_RUN_SCRIPT" > logs/dashboard.log 2>&1 &

echo "🎉 배포 완료!"
