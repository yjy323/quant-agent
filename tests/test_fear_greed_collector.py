# test_fear_greed_collector.py

"""
FearGreedDataCollector pytest 테스트 코드
"""

import json

from fear_greed_collector import FearGreedDataCollector


def test_fear_greed_data_collection():
    """공포탐욕지수 데이터 수집 및 출력 테스트"""
    collector = FearGreedDataCollector()
    result = collector.collect_fear_greed_data()

    print("\n" + "=" * 50)
    print("Fear & Greed Index Data:")
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 50)

    # pytest용 기본 검증
    assert result is not None
    assert isinstance(result, dict)
