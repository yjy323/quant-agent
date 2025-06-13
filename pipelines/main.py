"""
Data Pipeline Main Module

데이터 파이프라인의 메인 모듈입니다.

실행 방법:
프로젝트 루트에서: python -m data-pipeline.main
"""

from .collectors.chart_collector import ChartImageCollector
from .collectors.fear_greed_collector import FearGreedDataCollector
from .collectors.market_collector import CryptoDataCollector
from .collectors.news_collector import NewsCollector
from .collectors.youtube_collector import YouTubeCaptionsCollector
from .config import Config
from .storage.database_manager import DatabaseManager
from .utils.indicators.aggregator import IndicatorAggregator

# 외부 import 가능한 모듈들 명시
__all__ = [
    "Config",
    "CryptoDataCollector",
    "NewsCollector",
    "FearGreedDataCollector",
    "ChartImageCollector",
    "YouTubeCaptionsCollector",
    "DatabaseManager",
    "IndicatorAggregator",
]

if __name__ == "__main__":
    print("=== 데이터 파이프라인 시스템 ===")
    print("현재 모듈은 데이터 수집 시스템의 통합 모듈입니다.")
    print("각 수집기는 별도의 스케줄러에서 실행됩니다.")
    print("상세 실행은 별도 스크립트를 참조하세요.")
