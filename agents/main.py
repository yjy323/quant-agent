"""
투자 AI 엔진 메인 실행 파일
"""

from agents.agents.decision_agent import DecisionMaker
from agents.config import Config
from agents.services.trading_service import Trader
from pipelines.collectors.chart_collector import ChartImageCollector
from pipelines.collectors.market_collector import CryptoDataCollector
from pipelines.collectors.youtube_collector import YouTubeCaptionsCollector
from pipelines.storage.database_manager import DatabaseManager

# 외부에서 import 가능한 모듈들
__all__ = [
    "Config",
    "DecisionMaker",
    "Trader",
    "CryptoDataCollector",
    "ChartImageCollector",
    "YouTubeCaptionsCollector",
    "DatabaseManager",
]

if __name__ == "__main__":
    print("🤖 투자 AI 엔진 시스템")
    print("이 파일은 AI 투자 결정 시스템의 엔트리포인트입니다.")
    print("legacy_main.py를 실행하여 기존 시스템을 테스트하거나")
    print("새로운 멀티 에이전트 시스템을 실행하세요.")
