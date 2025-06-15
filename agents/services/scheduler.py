from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from agents.config import Config
from agents.core.investment_bot import InvestmentBot


class TradingScheduler:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()
        self.bot: Optional[InvestmentBot] = None
        self.is_active = False

    def trading_cycle_job(self) -> None:
        """거래 사이클 실행 작업"""
        try:
            if self.bot:
                self.bot.run_single_cycle()
        except Exception as e:
            print(f"❌ 거래 사이클 실행 중 오류: {e}")
            print("🔄 다음 사이클에서 재시도...")

    def start(self) -> bool:
        """거래 봇 시작"""
        if self.is_active:
            print("❌ 스케줄러가 이미 실행 중입니다")
            return False  # 이미 실행 중

        print("🚀 거래 봇 스케줄러 시작")
        print(f"📋 설정된 거래 간격: {Config.TRADING_INTERVAL_SECONDS}초")

        self.bot = InvestmentBot()
        print("✅ InvestmentBot 인스턴스 생성 완료")

        # 거래 사이클 작업 추가
        print("📝 APScheduler에 거래 사이클 작업 추가 중...")
        self.scheduler.add_job(
            self.trading_cycle_job,
            trigger=IntervalTrigger(seconds=Config.TRADING_INTERVAL_SECONDS),
            id="trading_cycle",
            name="Trading Cycle",
            replace_existing=True,
        )
        print("✅ 거래 사이클 작업 추가 완료")

        print("🔄 APScheduler 시작 중...")
        self.scheduler.start()
        print("✅ APScheduler 시작 완료")

        # 등록된 작업 확인
        jobs = self.scheduler.get_jobs()
        print(f"📊 등록된 작업 수: {len(jobs)}")
        for job in jobs:
            print(f"   - 작업 ID: {job.id}")
            print(f"   - 작업 이름: {job.name}")
            print(f"   - 다음 실행 시간: {job.next_run_time}")

        self.is_active = True
        print("🎉 스케줄러 시작 완료!")
        return True

    def stop(self) -> bool:
        """거래 봇 중단"""
        if not self.is_active:
            return False  # 실행 중이 아님

        print("⏹️ 거래 봇 스케줄러 중단")
        self.scheduler.shutdown()
        self.is_active = False
        self.bot = None
        return True

    def is_running(self) -> bool:
        """현재 실행 상태 반환"""
        return self.is_active


# 전역 스케줄러 인스턴스
scheduler = TradingScheduler()
