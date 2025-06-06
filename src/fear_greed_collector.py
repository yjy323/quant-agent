# fear_greed_collector.py

from datetime import datetime, timezone
from typing import Any, Dict, List

import requests
from requests.exceptions import RequestException, Timeout


class FearGreedDataCollector:
    """
    Alternative.me의 Fear & Greed Index API를 통해 공포탐욕지수 데이터를 수집하는 클래스

    기능:
    - 7일간의 공포탐욕지수 데이터 수집
    - AI Agent가 활용할 수 있는 JSON 형식으로 데이터 구조화
    - 에러 처리 및 안전장치 내장
    - 기존 시스템 아키텍처와 일관성 유지
    """

    # API 엔드포인트 및 설정
    API_BASE_URL = "https://api.alternative.me/fng/"
    DEFAULT_LIMIT = 7  # 7일간 데이터
    REQUEST_TIMEOUT = 10  # 10초 타임아웃

    def __init__(self) -> None:
        """FearGreedDataCollector 초기화"""
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Quant-Agent/1.0", "Accept": "application/json"}
        )

    def _make_api_request(self, limit: int = DEFAULT_LIMIT) -> Dict[str, Any]:
        """
        Alternative.me API에 요청을 보내고 응답을 반환

        Args:
            limit: 가져올 데이터 개수 (기본값: 7일)

        Returns:
            Dict[str, Any]: API 응답 데이터

        Raises:
            Exception: API 요청 실패 시
        """
        try:
            params = {"limit": limit}
            response = self.session.get(
                self.API_BASE_URL, params=params, timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()

            # API 응답 유효성 검사
            if not isinstance(data, dict) or "data" not in data:
                raise ValueError("Invalid API response format")

            if not data["data"]:
                raise ValueError("Empty data received from API")

            return data

        except Timeout:
            raise Exception("API 요청 시간 초과")
        except RequestException as e:
            raise Exception(f"API 요청 실패: {e}")
        except ValueError as e:
            raise Exception(f"API 응답 데이터 오류: {e}")
        except Exception as e:
            raise Exception(f"예상치 못한 오류: {e}")

    def _process_fear_greed_data(
        self, raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        원시 API 데이터를 AI Agent가 활용하기 쉬운 형태로 가공

        Args:
            raw_data: API에서 받은 원시 데이터

        Returns:
            List[Dict[str, Any]]: 가공된 공포탐욕지수 데이터
        """
        processed_data: List[Dict[str, Any]] = []

        for item in raw_data:
            try:
                # 타임스탬프를 readable한 형태로 변환
                timestamp = int(item["timestamp"])
                date_str = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
                    "%Y-%m-%d"
                )

                # 수치값 검증 및 변환
                value = int(item["value"])
                if not (0 <= value <= 100):
                    print(f"⚠️  경고: 비정상적인 공포탐욕지수 값: {value}")

                processed_item = {
                    "date": date_str,
                    "timestamp": timestamp,
                    "value": value,
                    "classification": item["value_classification"],
                    "days_ago": len(processed_data),  # 0이 최신, 1이 하루 전, ...
                }

                processed_data.append(processed_item)

            except (KeyError, ValueError, TypeError) as e:
                print(f"⚠️  데이터 처리 오류 (건너뜀): {e}")
                continue

        return processed_data

    def _calculate_trend_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        7일간 공포탐욕지수의 트렌드 분석

        Args:
            data: 처리된 공포탐욕지수 데이터

        Returns:
            Dict[str, Any]: 트렌드 분석 결과
        """
        if len(data) < 2:
            return {
                "trend_direction": "insufficient_data",
                "trend_strength": 0,
                "average_7d": data[0]["value"] if data else 0,
                "volatility": 0,
                "consecutive_days": 0,
            }

        values = [item["value"] for item in data]

        # 7일 평균
        average_7d = sum(values) / len(values)

        # 변동성 (표준편차)
        variance = sum((x - average_7d) ** 2 for x in values) / len(values)
        volatility = variance**0.5

        # 트렌드 방향 및 강도
        latest_value = values[0]  # 가장 최신
        oldest_value = values[-1]  # 7일 전
        trend_change = latest_value - oldest_value

        if abs(trend_change) < 5:
            trend_direction = "sideways"
        elif trend_change > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"

        # 연속 같은 구간 일수 계산
        current_classification = data[0]["classification"]
        consecutive_days = 1
        for i in range(1, len(data)):
            if data[i]["classification"] == current_classification:
                consecutive_days += 1
            else:
                break

        return {
            "trend_direction": trend_direction,
            "trend_strength": abs(trend_change),
            "average_7d": round(average_7d, 2),
            "volatility": round(volatility, 2),
            "consecutive_days": consecutive_days,
            "current_vs_average": round(latest_value - average_7d, 2),
        }

    def collect_fear_greed_data(self) -> Dict[str, Any]:
        """
        공포탐욕지수 데이터를 수집하고 AI Agent용 JSON 형식으로 반환

        Returns:
            Dict[str, Any]: AI Agent가 활용할 수 있는 구조화된 공포탐욕지수 데이터
        """
        try:
            print("📊 공포탐욕지수 데이터 수집 중...")

            # API 요청
            raw_response = self._make_api_request(limit=self.DEFAULT_LIMIT)

            # 데이터 가공
            processed_data = self._process_fear_greed_data(raw_response["data"])

            if not processed_data:
                raise Exception("처리된 데이터가 없습니다")

            # 트렌드 분석
            trend_analysis = self._calculate_trend_analysis(processed_data)

            # 최종 결과 구성
            result = {
                "collection_timestamp": datetime.now(timezone.utc).isoformat(),
                "data_source": "alternative.me",
                "period_days": len(processed_data),
                "current_index": {
                    "value": processed_data[0]["value"],
                    "classification": processed_data[0]["classification"],
                    "date": processed_data[0]["date"],
                },
                "historical_data": processed_data,
                "trend_analysis": trend_analysis,
                "market_sentiment_summary": self._generate_sentiment_summary(
                    processed_data[0], trend_analysis
                ),
            }

            print(f"✅ 공포탐욕지수 데이터 수집 완료: {len(processed_data)}일간 데이터")
            return result

        except Exception as e:
            print(f"❌ 공포탐욕지수 데이터 수집 실패: {e}")
            return self._get_fallback_data()

    def _generate_sentiment_summary(
        self, current_data: Dict[str, Any], trend_analysis: Dict[str, Any]
    ) -> str:
        """
        현재 시장 심리를 요약하는 문장 생성

        Args:
            current_data: 현재 공포탐욕지수 데이터
            trend_analysis: 트렌드 분석 결과

        Returns:
            str: 시장 심리 요약
        """
        value = current_data["value"]
        classification = current_data["classification"]
        trend = trend_analysis["trend_direction"]
        consecutive = trend_analysis["consecutive_days"]

        summary = f"현재 {classification} 상태({value})이며, "

        if trend == "increasing":
            summary += f"지난 7일간 상승 추세로 {consecutive}일 연속 유지"
        elif trend == "decreasing":
            summary += f"지난 7일간 하락 추세로 {consecutive}일 연속 유지"
        else:
            summary += f"지난 7일간 횡보 상태로 {consecutive}일 연속 유지"

        return summary

    def _get_fallback_data(self) -> Dict[str, Any]:
        """
        API 요청 실패 시 사용할 기본 데이터

        Returns:
            Dict[str, Any]: 기본 응답 데이터
        """
        return {
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "data_source": "fallback",
            "period_days": 0,
            "current_index": {
                "value": 50,
                "classification": "Neutral",
                "date": datetime.now().strftime("%Y-%m-%d"),
            },
            "historical_data": [],
            "trend_analysis": {
                "trend_direction": "unknown",
                "trend_strength": 0,
                "average_7d": 50,
                "volatility": 0,
                "consecutive_days": 0,
                "current_vs_average": 0,
            },
            "market_sentiment_summary": "API 데이터 수집 실패로 중립 상태로 가정",
            "error": "Fear & Greed Index API 접근 불가",
        }

    def __del__(self) -> None:
        """소멸자: 세션 정리"""
        if hasattr(self, "session"):
            self.session.close()
