from typing import Any

import pyupbit  # type: ignore
import ta  # type: ignore

from config import Config


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
                "market": orderbook[0]["market"],
                "timestamp": orderbook[0]["timestamp"],
                "total_ask_size": orderbook[0]["total_ask_size"],
                "total_bid_size": orderbook[0]["total_bid_size"],
                "top_5_orderbook": orderbook[0]["orderbook_units"][:5],
            }
        except Exception as e:
            print(f"오더북 데이터 조회 중 오류 발생: {e}")
            return None

    def _add_technical_indicators(self, df: Any) -> Any:
        """기술적 지표 추가 (ta 라이브러리 사용)"""
        try:
            if df is None or df.empty:
                return df

            # 데이터 유효성 검사
            required_columns = ["open", "high", "low", "close", "volume"]
            if not all(col in df.columns for col in required_columns):
                print("필수 컬럼이 누락되었습니다.")
                return df

            # Moving Averages
            df["SMA_10"] = ta.trend.sma_indicator(df["close"], window=10)
            df["EMA_10"] = ta.trend.ema_indicator(df["close"], window=10)

            # RSI
            df["RSI_14"] = ta.momentum.rsi(df["close"], window=14)

            # Stochastic Oscillator
            df["STOCH_K"] = ta.momentum.stoch(
                df["high"], df["low"], df["close"], window=14, smooth_window=3
            )
            df["STOCH_D"] = ta.momentum.stoch_signal(
                df["high"], df["low"], df["close"], window=14, smooth_window=3
            )

            # MACD (ta 라이브러리 사용)
            df["MACD"] = ta.trend.macd(df["close"], window_slow=26, window_fast=12)
            df["MACD_Signal"] = ta.trend.macd_signal(
                df["close"], window_slow=26, window_fast=12, window_sign=9
            )
            df["MACD_Histogram"] = ta.trend.macd_diff(
                df["close"], window_slow=26, window_fast=12, window_sign=9
            )

            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(
                df["close"], window=20, window_dev=2
            )
            df["Upper_Band"] = bollinger.bollinger_hband()
            df["Middle_Band"] = bollinger.bollinger_mavg()
            df["Lower_Band"] = bollinger.bollinger_lband()

            return df

        except Exception as e:
            print(f"기술적 지표 계산 중 오류 발생: {e}")
            return df

    def _get_ohlcv_data(self) -> dict:
        """OHLCV 데이터 수집 및 기술적 지표 추가"""
        try:
            # 일봉 데이터
            df_daily = pyupbit.get_ohlcv(
                self.ticker, interval="day", count=Config.DAILY_DATA_COUNT
            )
            if df_daily is not None and not df_daily.empty:
                df_daily = self._add_technical_indicators(df_daily)

            # 시간봉 데이터
            df_hourly = pyupbit.get_ohlcv(
                self.ticker, interval="minute60", count=Config.HOURLY_DATA_COUNT
            )
            if df_hourly is not None and not df_hourly.empty:
                df_hourly = self._add_technical_indicators(df_hourly)

            return {"daily_ohlcv": df_daily, "hourly_ohlcv": df_hourly}

        except Exception as e:
            print(f"OHLCV 데이터 수집 중 오류 발생: {e}")
            return {"daily_ohlcv": None, "hourly_ohlcv": None}

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
