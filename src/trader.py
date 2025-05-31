from typing import Any

import pyupbit  # type: ignore

from config import Config


class Trader:
    def __init__(self, upbit: Any) -> None:
        self.upbit = upbit
        self.ticker: str = Config.TICKER
        self.min_amount: float = Config.MINIMUM_TRADE_AMOUNT
        self.fee_rate: float = Config.TRADING_FEE_RATE

    def execute_buy(self) -> Any:
        """매수 실행"""

        try:
            krw_balance = self.upbit.get_balance("KRW")
            available_krw = krw_balance * (1 - self.fee_rate)

            if available_krw > self.min_amount:
                result = self.upbit.buy_market_order(self.ticker, available_krw)
                print(f"✅ 매수 주문 실행: {result}")
                return result
            else:
                print(
                    f"❌ 매수 실패: 잔고 부족 (보유: {krw_balance:,.0f}원, 필요: "
                    f"{self.min_amount:,}원)"
                )
                return None

        except Exception as e:
            print(f"❌ 매수 주문 실행 오류: {e}")
            return None

    def execute_sell(self) -> Any:
        """매도 실행"""
        try:
            btc_balance = self.upbit.get_balance("BTC")
            current_price = pyupbit.get_current_price(self.ticker)
            sell_value = btc_balance * current_price

            if sell_value > self.min_amount:
                result = self.upbit.sell_market_order(self.ticker, btc_balance)
                print(f"✅ 매도 주문 실행: {result}")
                return result
            else:
                print(
                    f"❌ 매도 실패: 잔고 부족 (보유가치: {sell_value:,.0f}원, 필요: "
                    f"{self.min_amount:,}원)"
                )
                return None

        except Exception as e:
            print(f"❌ 매도 주문 실행 오류: {e}")
            return None

    def execute_decision(self, ai_decision: dict) -> Any:
        """AI 결정에 따른 거래 실행"""
        decision = ai_decision.get("decision", "hold")

        if decision == "buy":
            return self.execute_buy()
        elif decision == "sell":
            return self.execute_sell()
        else:
            print("🔄 보유 결정 - 거래 없음")
            return None
