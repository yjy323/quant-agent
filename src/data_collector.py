from typing import Any

import pyupbit  # type: ignore

from config import Config

# 새로운 지표 모듈 임포트
from indicators.aggregator import IndicatorAggregator
from indicators.bollinger import BollingerIndicator
from indicators.exceptions import IndicatorError
from indicators.macd import MACDIndicator
from indicators.moving_average import MovingAverageIndicator
from indicators.rsi import RSIIndicator


class CryptoDataCollector:
    def __init__(self, upbit: Any) -> None:
        self.ticker: str = Config.TICKER
        self.upbit = upbit

    def _get_investment_status(self) -> dict | None:
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

    def collect_all_data(self) -> dict | None:
        """모든 데이터 수집"""
        try:
            investment_status = self._get_investment_status()
            orderbook_data = self._get_orderbook_data()
            ohlcv_data = self._get_ohlcv_data()

            return {
                "investment_status": investment_status,
                "orderbook": orderbook_data,
                "market_data": ohlcv_data,
            }
        except Exception as e:
            print(f"전체 데이터 수집 중 오류 발생: {e}")
            return None
