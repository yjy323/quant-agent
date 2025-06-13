# data_collector.py (뉴스 기능 통합)

import json
from datetime import datetime
from typing import Any, cast

import pyupbit  # type: ignore

from ..config import Config

# 새로운 지표 모듈 임포트
from ..utils.indicators.aggregator import IndicatorAggregator
from ..utils.indicators.bollinger import BollingerIndicator
from ..utils.indicators.exceptions import IndicatorError
from ..utils.indicators.macd import MACDIndicator
from ..utils.indicators.moving_average import MovingAverageIndicator
from ..utils.indicators.rsi import RSIIndicator
from .fear_greed_collector import FearGreedDataCollector
from .news_collector import NewsCollector  # 새로 추가


class CryptoDataCollector:
    def __init__(self, upbit: Any) -> None:
        self.ticker: str = Config.TICKER
        self.upbit = upbit
        self.fear_greed_collector = FearGreedDataCollector()
        self.news_collector = NewsCollector()  # 뉴스 수집기 추가

    def _get_investment_status(self) -> dict[str, Any] | None:
        """현재 투자 상태 조회"""
        try:
            balances = self.upbit.get_balances()
            if not balances:
                print("잔고 정보를 가져올 수 없습니다.")
                return None

            investment_status = {
                "krw_balance": 0.0,
                "btc_balance": 0.0,
                "btc_avg_buy_price": 0.0,
                "total_krw_value": 0.0,
                "btc_current_price": 0.0,
                "profit_loss": 0.0,
                "profit_loss_rate": 0.0,
            }

            # 현재 BTC 시세 조회 (정적 메서드 사용)
            btc_current_price = pyupbit.get_current_price(self.ticker)
            if btc_current_price is None:
                print("현재가 정보를 가져올 수 없습니다.")
                return None

            investment_status["btc_current_price"] = btc_current_price

            for balance in balances:
                if balance["currency"] == "KRW":
                    investment_status["krw_balance"] = float(balance["balance"])
                elif balance["currency"] == "BTC":
                    investment_status["btc_balance"] = float(balance["balance"])
                    investment_status["btc_avg_buy_price"] = float(
                        balance["avg_buy_price"]
                    )

            # 총 자산 가치 계산
            btc_krw_value = investment_status["btc_balance"] * btc_current_price
            investment_status["total_krw_value"] = (
                investment_status["krw_balance"] + btc_krw_value
            )

            # 손익 계산
            if (
                investment_status["btc_balance"] > 0
                and investment_status["btc_avg_buy_price"] > 0
            ):
                cost_basis = (
                    investment_status["btc_balance"]
                    * investment_status["btc_avg_buy_price"]
                )
                current_value = investment_status["btc_balance"] * btc_current_price
                investment_status["profit_loss"] = current_value - cost_basis
                investment_status["profit_loss_rate"] = (
                    investment_status["profit_loss"] / cost_basis
                ) * 100

            return investment_status

        except Exception as e:
            print(f"투자 상태 조회 중 오류 발생: {e}")
            return None

    def _get_orderbook_data(self) -> dict | None:
        """오더북 데이터 조회"""
        try:
            # 정적 메서드 사용 (ticker 파라미터 이름 주의)
            orderbook = pyupbit.get_orderbook(ticker=self.ticker)
            if not orderbook:
                return None

            return {
                "market": orderbook["market"],
                "timestamp": orderbook["timestamp"],
                "total_ask_size": orderbook["total_ask_size"],
                "total_bid_size": orderbook["total_bid_size"],
                "top_5_orderbook": orderbook["orderbook_units"][:5],
            }
        except Exception as e:
            print(f"오더북 데이터 조회 중 오류 발생: {e}")
            return None

    def _calculate_technical_indicators(self, df: Any) -> dict[str, Any]:
        """새로운 지표 계산 메서드 (기존 _add_technical_indicators 대체)"""
        try:
            if df is None or df.empty:
                print("지표 계산용 데이터가 비어있습니다.")
                return {}

            # 데이터 유효성 검사
            required_columns = ["open", "high", "low", "close", "volume"]
            if not all(col in df.columns for col in required_columns):
                print("필수 컬럼이 누락되었습니다.")
                return {}

            # 지표 인스턴스 생성
            indicators = [
                MovingAverageIndicator(df),
                RSIIndicator(df),
                MACDIndicator(df),
                BollingerIndicator(df),
            ]

            # 통합 계산 (full_series=False로 최신값만)
            aggregator = IndicatorAggregator(indicators)
            result = aggregator.aggregate(full_series=False)

            print(f"✅ 기술적 지표 계산 완료: {list(result.keys())}")
            return dict(result)  # Ensure result is a dict[str, Any]

        except IndicatorError as e:
            print(f"지표 계산 오류: {e}")
            return {}
        except Exception as e:
            print(f"지표 계산 중 예상치 못한 오류: {e}")
            return {}

    def _get_ohlcv_data(self) -> dict:
        """OHLCV 데이터 수집 및 기술적 지표 추가"""
        try:
            # 일봉 데이터
            df_daily = pyupbit.get_ohlcv(
                self.ticker, interval="day", count=Config.DAILY_DATA_COUNT
            )
            daily_indicators = {}
            if df_daily is not None and not df_daily.empty:
                daily_indicators = self._calculate_technical_indicators(df_daily)

            # 시간봉 데이터
            df_hourly = pyupbit.get_ohlcv(
                self.ticker, interval="minute60", count=Config.HOURLY_DATA_COUNT
            )
            hourly_indicators = {}
            if df_hourly is not None and not df_hourly.empty:
                hourly_indicators = self._calculate_technical_indicators(df_hourly)

            return {
                "daily_ohlcv": df_daily,
                "hourly_ohlcv": df_hourly,
                "daily_indicators": daily_indicators,
                "hourly_indicators": hourly_indicators,
            }

        except Exception as e:
            print(f"OHLCV 데이터 수집 중 오류 발생: {e}")
            return {
                "daily_ohlcv": None,
                "hourly_ohlcv": None,
                "daily_indicators": {},
                "hourly_indicators": {},
            }

    def _format_ohlcv_for_ai(self, df: Any) -> dict | None:
        """OHLCV DataFrame을 AI가 이해할 수 있는 JSON 형태로 변환"""
        try:
            if df is None or df.empty:
                return None

            # 최근 5개 데이터만 선택하여 JSON 변환
            recent_data = df.tail(5).to_json(orient="index", date_format="iso")
            return cast(dict[str, Any], json.loads(recent_data))
        except Exception as e:
            print(f"OHLCV 데이터 포맷팅 오류: {e}")
            return None

    def _collect_news_data(self) -> dict[str, Any]:
        """뉴스 데이터 수집 (새로 추가)"""
        try:
            news_data = self.news_collector.collect_bitcoin_news()
            return cast(dict[str, Any], news_data)
        except Exception as e:
            print(f"뉴스 데이터 수집 중 오류 발생: {e}")
            # 뉴스 수집 실패 시 빈 데이터 반환
            return {
                "collection_timestamp": datetime.now().isoformat(),
                "final_count": 0,
                "news_articles": [],
            }

    def collect_all_data(self) -> str:
        """
        모든 데이터 수집 및 AI 분석용 JSON 문자열 반환

        Returns:
            str: AI가 분석할 수 있는 JSON 형식의 문자열
        """
        print("📡 데이터 수집 중...")

        # 1. 기본 데이터 수집
        investment_status = self._get_investment_status()
        orderbook_data = self._get_orderbook_data()
        ohlcv_data = self._get_ohlcv_data()

        # 2. 공포탐욕지수 데이터 수집
        fear_greed_data = self.fear_greed_collector.collect_fear_greed_data()

        # 3. 뉴스 데이터 수집 (새로 추가)
        news_data = self._collect_news_data()

        # 4. AI용 OHLCV 데이터 포맷팅
        daily_ohlcv_formatted = self._format_ohlcv_for_ai(ohlcv_data["daily_ohlcv"])
        hourly_ohlcv_formatted = self._format_ohlcv_for_ai(ohlcv_data["hourly_ohlcv"])

        # 5. AI 분석용 최종 데이터 구성
        ai_formatted_data = {
            "analysis_timestamp": datetime.now().isoformat(),
            "investment_status": investment_status,
            "orderbook": orderbook_data,
            "market_data": {
                "daily_ohlcv_recent": daily_ohlcv_formatted,
                "hourly_ohlcv_recent": hourly_ohlcv_formatted,
                "daily_indicators": ohlcv_data["daily_indicators"],
                "hourly_indicators": ohlcv_data["hourly_indicators"],
            },
            "fear_greed_index": fear_greed_data,
            "news_analysis": news_data,  # 뉴스 데이터 추가
        }

        # 6. JSON 문자열로 변환하여 반환
        json_data = json.dumps(ai_formatted_data, ensure_ascii=False, indent=2)
        print("✅ AI용 데이터 포맷팅 완료")
        return json_data
