import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
    UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")

    # Trading Settings
    TICKER = "KRW-BTC"
    MINIMUM_TRADE_AMOUNT = 5000
    TRADING_FEE_RATE = 0.0005  # 0.05%

    # Data Settings
    DAILY_DATA_COUNT = 60
    HOURLY_DATA_COUNT = 60

    # AI Model Settings
    AI_MODEL = "gpt-4.1"
    INSTRUCTIONS_FILE = "instructions.md"

    # Trading Schedule
    TRADING_INTERVAL_SECONDS = 60

    # Selenium Settings
    UPBIT_CHART_URL = "https://upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC"
    # CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver" # 필요시 주석 해제 및 경로 설정
    SELENIUM_HEADLESS = True  # True로 설정하면 GUI 없이 백그라운드에서 실행
    SELENIUM_TIMEOUT = 10  # Selenium 요소 탐색 타임아웃

    # Chart Image Storage Settings
    CHART_IMAGES_DIR = Path("data/encoded_images")
    CHART_IMAGE_FILENAME_FORMAT = "chart_{symbol}_{timeframe}_{timestamp}.txt"

    @classmethod
    def ensure_chart_images_dir(cls) -> Path:
        cls.CHART_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        return cls.CHART_IMAGES_DIR
