#!/bin/bash

set -e  # 에러 발생 시 즉시 종료
echo "🚀 Quant-Agent 시스템 배포 시작"

# 경로 설정
PROJECT_DIR="/home/ubuntu/quant-agent"
VENV_DIR="$PROJECT_DIR/.venv"
DATA_PIPELINE="$PROJECT_DIR/pipelines"
INVESTMENT_ENGINE="$PROJECT_DIR/agents"
DASHBOARD_DIR="$PROJECT_DIR/dashboards"
LOGS_DIR="$PROJECT_DIR/logs"

# 로그 디렉토리 생성
mkdir -p "$LOGS_DIR"

echo "📦 가상환경 활성화 및 의존성 설치"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo "🧹 실행 중인 프로세스 종료"
# 기존 프로세스들 종료
pkill -f "pipelines" || echo "ℹ️ pipelines 프로세스 없음"
pkill -f "agents" || echo "ℹ️ agents 프로세스 없음"
pkill -f "legacy_main.py" || echo "ℹ️ legacy_main.py 프로세스 없음"
pkill -f streamlit || echo "ℹ️ streamlit 프로세스 없음"

echo "🔄 데이터 파이프라인 시스템 시작"
# 데이터 파이프라인은 별도 스케줄러로 실행 (향후 구현)
# 현재는 legacy 시스템 사용
echo "📊 투자 AI 엔진 시스템 (Legacy) 시작"
cd "$PROJECT_DIR"
nohup python3 "$INVESTMENT_ENGINE/legacy_main.py" > "$LOGS_DIR/investment-engine.log" 2>&1 &

echo "📈 대시보드 시스템 시작"
cd "$DASHBOARD_DIR"
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > "$LOGS_DIR/dashboard.log" 2>&1 &

# 프로세스 상태 확인
sleep 3
echo "🔍 실행 중인 프로세스 확인:"
ps aux | grep -E "(legacy_main|streamlit)" | grep -v grep || echo "⚠️ 프로세스를 찾을 수 없습니다"

echo "📁 로그 파일 위치:"
echo "  - 투자 엔진: $LOGS_DIR/investment-engine.log"
echo "  - 대시보드: $LOGS_DIR/dashboard.log"

echo "🎉 배포 완료!"
echo "📊 대시보드 접속: http://서버IP:8501"
