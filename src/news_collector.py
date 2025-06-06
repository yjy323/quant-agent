# news_collector.py

from datetime import datetime, timezone
from typing import Any, Dict

import serpapi

from config import Config


class NewsCollector:
    """비트코인 뉴스 수집 클래스"""

    def __init__(self) -> None:
        api_key = Config.SERPAPI_KEY
        if not api_key:
            raise ValueError("SERPAPI_KEY 환경변수가 설정되지 않았습니다.")

        self.client = serpapi.Client(api_key=api_key)

    def collect_bitcoin_news(self) -> Dict[str, Any]:
        """비트코인 뉴스 수집 및 JSON 반환"""
        print("📰 비트코인 뉴스 수집 중...")

        try:
            # SerpAPI Google News 검색
            results = self.client.search(
                engine="google_news", q="bitcoin", gl="us", hl="en"
            )

            # 뉴스 결과 추출
            news_results = results.get("news_results", [])

            # 상위 5개 선택
            top_news = news_results[:5]

            # 간단한 데이터 가공
            processed_news = []
            for i, news in enumerate(top_news, 1):
                processed_news.append(
                    {
                        "rank": i,
                        "title": news.get("title", ""),
                        "snippet": news.get("snippet", ""),
                        "source": (
                            news.get("source", {}).get("name", "")
                            if isinstance(news.get("source"), dict)
                            else str(news.get("source", ""))
                        ),
                        "date": news.get("date", ""),
                        "link": news.get("link", ""),
                    }
                )

            # 최종 결과
            result = {
                "collection_timestamp": datetime.now(timezone.utc).isoformat(),
                "final_count": len(processed_news),
                "news_articles": processed_news,
            }

            print(f"✅ 비트코인 뉴스 수집 완료: {len(processed_news)}개")
            return result

        except Exception as e:
            print(f"❌ 뉴스 수집 실패: {e}")
            return {
                "collection_timestamp": datetime.now(timezone.utc).isoformat(),
                "final_count": 0,
                "news_articles": [],
            }
