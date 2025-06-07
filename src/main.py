# main.py

import time
from datetime import datetime
from typing import Any, Dict

import pyupbit  # type: ignore

from chart_image_collector import ChartImageCollector
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
        self.chart_collector = ChartImageCollector()

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
        # 1. 수치 데이터 수집
        print("📡 수치 데이터 수집 중...")
        ai_formatted_data = self.crypto_data_collector.collect_all_data()

        # 2. 차트 이미지 수집
        print("📸 차트 이미지 수집 중...")
        chart_result = self.chart_collector.collect_1m_chart()
        chart_file_path = chart_result["chart_file_path"] if chart_result else None

        # 3. 상태 출력
        status_data = self.crypto_data_collector._get_investment_status()
        if status_data:
            self.print_status(status_data)

        # 4. AI 분석
        print("🤖 AI 분석 중 (수치 데이터 + 차트 이미지)...")
        ai_decision = self.decision_maker.analyze(ai_formatted_data, chart_file_path)

        # 5. AI 결정 출력
        print(f"🎯 AI 결정: {ai_decision.get('decision', 'unknown').upper()}")

        ratio = ai_decision.get("ratio", 0)
        if ratio > 0:
            action_type = "투자" if ai_decision.get("decision") == "buy" else "매도"
            print(f"📊 {action_type} 비율: {ratio}%")

        print(f"📝 근거: {ai_decision.get('reason', 'No reason provided')}")

        # 6. 거래 실행
        print("\n💼 거래 실행...")
        self.trader.execute_decision(ai_decision)

    def run(self) -> None:
        """메인 실행 루프"""
        print("🚀 비트코인 AI 자동매매 봇 시작")
        print(f"🔄 거래 간격: {Config.TRADING_INTERVAL_SECONDS}초")
        print("-" * 60)

        while True:
            self.run_single_cycle()
            print(f"\n⏰ {Config.TRADING_INTERVAL_SECONDS}초 대기 중...")
            print("-" * 60)
            time.sleep(Config.TRADING_INTERVAL_SECONDS)


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
