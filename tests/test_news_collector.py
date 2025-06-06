#!/usr/bin/env python3
# simple_news_test.py

import json

from news_collector import NewsCollector


def test_news_collector():
    print("📰 비트코인 뉴스 수집 테스트")
    print("-" * 50)

    try:
        # NewsCollector 생성 및 뉴스 수집
        collector = NewsCollector()
        news_data = collector.collect_bitcoin_news()

        # 기본 검증
        assert isinstance(news_data, dict), "뉴스 데이터는 dict 타입이어야 합니다"
        assert "news_articles" in news_data, "news_articles 키가 존재해야 합니다"

        # 결과 출력
        print("✅ 검증 통과!")
        print(json.dumps(news_data, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
