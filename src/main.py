import time
from datetime import datetime
from typing import Any, Dict

import pyupbit  # type: ignore

from config import Config
from data_collector import CryptoDataCollector
from decision_maker import DecisionMaker
from trader import Trader


class TradingBot:
    def __init__(self) -> None:
        self.upbit = pyupbit.Upbit(Config.UPBIT_ACCESS_KEY, Config.UPBIT_SECRET_KEY)
        self.crypto_data_collector = CryptoDataCollector(self.upbit)
        self.decision_maker = DecisionMaker()
        self.trader = Trader(self.upbit)

    def print_status(self, investment_status: Dict[str, Any]) -> None:
        """현재 상태 출력"""
        print("\n" + "=" * 60)
        print(f"📊 투자 상태 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("=" * 60)
        print(f"💰 KRW 잔고: {investment_status['krw_balance']:,.0f}원")
        print(f"₿  BTC 잔고: {investment_status['btc_balance']:.8f} BTC")
        print(f"📈 BTC 현재가: {investment_status['btc_current_price']:,.0f}원")
        print(f"💼 총 자산: {investment_status['total_krw_value']:,.0f}원")

        if investment_status["btc_balance"] > 0:
            print(f"📊 평균매수가: {investment_status['btc_avg_buy_price']:,.0f}원")
            print(
                f"💹 손익: {investment_status['profit_loss']:,.0f}원 ("
                f"{investment_status['profit_loss_rate']:.2f}%)"
            )
        print("=" * 60)

    def run_single_cycle(self) -> None:
        """단일 거래 사이클 실행"""
        try:
            # 1. 데이터 수집
            print("📡 데이터 수집 중...")
            collected_data = self.crypto_data_collector.collect_all_data()
            if not collected_data or not collected_data.get("investment_status"):
                print("❌ 데이터 수집 실패. 사이클 종료.")
                return

            # 2. 현재 상태 출력
            self.print_status(collected_data["investment_status"])

            # 3. AI 분석
            print("🤖 AI 분석 중...")
            ai_decision = self.decision_maker.analyze(collected_data)

            # 4. AI 결정 출력
            print(f"🎯 AI 결정: {ai_decision.get('decision', 'unknown').upper()}")
            print(f"📝 근거: {ai_decision.get('reason', 'No reason provided')}")

            # 5. 거래 실행
            print("\n💼 거래 실행...")
            self.trader.execute_decision(ai_decision)

        except Exception as e:
            print(f"❌ 거래 사이클 오류: {e}")

    def run(self) -> None:
        """메인 실행 루프"""
        print("🚀 비트코인 AI 자동매매 봇 시작")
        print(f"🔄 거래 간격: {Config.TRADING_INTERVAL_SECONDS}초")

        while True:
            try:
                self.run_single_cycle()
                print(f"\n⏰ {Config.TRADING_INTERVAL_SECONDS}초 대기 중...")
                time.sleep(Config.TRADING_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                print("\n🛑 프로그램 종료")
                break
            except Exception as e:
                print(f"❌ 메인 루프 오류: {e}")
                print(f"⏰ {Config.TRADING_INTERVAL_SECONDS}초 후 재시도...")
                time.sleep(Config.TRADING_INTERVAL_SECONDS)


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
