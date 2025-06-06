import os

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
