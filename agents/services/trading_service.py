# trader.py (Refactored)

from typing import Any

import pyupbit  # type: ignore
from config import Config


class Trader:
    def __init__(self, upbit: Any) -> None:
        self.upbit = upbit
        self.ticker: str = Config.TICKER
        self.min_amount: float = Config.MINIMUM_TRADE_AMOUNT
        self.fee_rate: float = Config.TRADING_FEE_RATE

    def execute_decision(self, ai_decision: dict) -> Any:
        """AI 결정에 따른 거래 실행"""
        decision = ai_decision.get("decision", "hold")
        ratio = ai_decision.get("ratio", 0)

        if decision == "buy":
            return self.execute_buy(ratio)
        elif decision == "sell":
            return self.execute_sell(ratio)
        else:
            print("🔄 보유 결정 - 거래 없음")
            return None

    def execute_buy(self, ratio: float) -> Any:
        """비율에 따른 매수 실행"""
        if ratio <= 0:
            print("🔄 매수 비율 0% - 거래 없음")
            return None

        krw_balance = self.upbit.get_balance("KRW")
        available_krw = krw_balance * (1 - self.fee_rate)
        buy_amount = available_krw * (ratio / 100)

        if buy_amount > self.min_amount:
            result = self.upbit.buy_market_order(self.ticker, buy_amount)
            print(f"✅ 매수 주문 실행 ({ratio}%): {result}")
            return result
        else:
            print(
                f"❌ 매수 실패: 거래금액 부족 "
                f"(계산된 금액: {buy_amount:,.0f}원, "
                f"최소: {self.min_amount:,}원)"
            )
            return None

    def execute_sell(self, ratio: float) -> Any:
        """비율에 따른 매도 실행"""
        if ratio <= 0:
            print("🔄 매도 비율 0% - 거래 없음")
            return None

        btc_balance = self.upbit.get_balance("BTC")
        sell_amount = btc_balance * (ratio / 100)
        current_price = pyupbit.get_current_price(self.ticker)
        sell_value = sell_amount * current_price

        if sell_value > self.min_amount:
            result = self.upbit.sell_market_order(self.ticker, sell_amount)
            print(f"✅ 매도 주문 실행 ({ratio}%): {result}")
            return result
        else:
            print(
                f"❌ 매도 실패: 거래금액 부족 "
                f"(계산된 금액: {sell_value:,.0f}원, "
                f"최소: {self.min_amount:,}원)"
            )
            return None
