# main.py (YouTube Integration)

import time
from datetime import datetime
from typing import Any, Dict

import pyupbit  # type: ignore

from chart_image_collector import ChartImageCollector
from config import Config
from data_collector import CryptoDataCollector
from decision_maker import DecisionMaker
from trader import Trader
from youtube_captions_collector import YouTubeCaptionsCollector


class TradingBot:
    def __init__(self) -> None:
        self.upbit = pyupbit.Upbit(Config.UPBIT_ACCESS_KEY, Config.UPBIT_SECRET_KEY)
        self.crypto_data_collector = CryptoDataCollector(self.upbit)
        self.decision_maker = DecisionMaker()
        self.trader = Trader(self.upbit)
        self.chart_collector = ChartImageCollector()
        self.youtube_collector = YouTubeCaptionsCollector()

    def print_status(self, investment_status: Dict[str, Any]) -> None:
        """현재 상태 출력"""
        print("\n" + "=" * 70)
        print(f"📊 투자 상태 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("=" * 70)
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
        print("=" * 70)

    def run_single_cycle(self) -> None:
        """단일 거래 사이클 실행"""
        print(f"\n🚀 거래 사이클 시작 ({datetime.now().strftime('%H:%M:%S')})")

        # 1. 수치 데이터 수집
        print("📡 수치 데이터 수집 중...")
        ai_formatted_data = self.crypto_data_collector.collect_all_data()

        # 2. 차트 이미지 수집
        print("📸 차트 이미지 수집 중...")
        chart_result = self.chart_collector.collect_1m_chart()
        chart_file_path = chart_result["chart_file_path"] if chart_result else None

        # 3. YouTube 자막 수집
        print("📺 YouTube 자막 수집 중...")
        youtube_data = self.youtube_collector.collect_captions()

        # 4. 투자 상태 출력
        status_data = self.crypto_data_collector._get_investment_status()
        if status_data:
            self.print_status(status_data)

        # 5. AI 종합 분석
        print("🤖 AI 종합 분석 중...")
        ai_decision = self.decision_maker.analyze(
            ai_formatted_data, chart_file_path, youtube_data
        )

        # 6. AI 결정 출력
        self._print_ai_decision(ai_decision)

        # 7. 거래 실행
        print("\n💼 거래 실행...")
        trade_result = self.trader.execute_decision(ai_decision)
        if trade_result:
            print(f"✅ 거래 완료: {trade_result}")

    def _print_ai_decision(self, ai_decision: Dict[str, Any]) -> None:
        """AI 결정 상세 출력"""
        print("\n" + "🎯" * 25 + " AI 분석 결과 " + "🎯" * 25)

        decision = ai_decision.get("decision", "unknown").upper()
        ratio = ai_decision.get("ratio", 0)
        reason = ai_decision.get("reason", "No reason provided")

        # 결정 출력
        decision_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(decision, "❓")
        print(f"{decision_emoji} **결정**: {decision}")

        if ratio > 0:
            action_type = "투자" if decision == "BUY" else "매도"
            print(f"📊 **{action_type} 비율**: {ratio}%")

        print(f"📝 **근거**: {reason}")

        # 분석 요소별 결과
        if ai_decision.get("chart_analysis"):
            print(f"📊 **차트 분석**: {ai_decision['chart_analysis']}")

        if ai_decision.get("youtube_analysis"):
            print(f"📺 **YouTube 분석**: {ai_decision['youtube_analysis']}")

        print("🎯" * 65)

    def run(self) -> None:
        """메인 실행 루프"""
        print("🚀 비트코인 AI 자동매매 봇 시작 (YouTube 분석 통합)")
        print(f"🔄 거래 간격: {Config.TRADING_INTERVAL_SECONDS}초")
        print("-" * 70)

        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                print(f"\n📅 사이클 #{cycle_count}")
                self.run_single_cycle()

            except KeyboardInterrupt:
                print("\n⏹️ 사용자에 의해 중단됨")
                break
            except Exception as e:
                print(f"❌ 사이클 실행 중 오류: {e}")
                print("🔄 다음 사이클에서 재시도...")

            print(f"\n⏰ {Config.TRADING_INTERVAL_SECONDS}초 대기 중...")
            print("-" * 70)
            time.sleep(Config.TRADING_INTERVAL_SECONDS)


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
