# indicator_module/config.py

"""
─────────────────────────────────────────────────────────────────────────────────────────────────
  indicator_module/config.py

  • 이 파일은 각종 보조 지표(Indicator) 클래스에서 사용하는 기본 파라미터(윈도우 크기, 표준편차 배수 등)를
    중앙집중식으로 관리합니다.
  • 환경변수를 통해서도 값을 덮어쓸 수 있도록 설계되어 있어, 운영 환경이나 테스트 환경에 맞춰 유연하게 조정할 수 있습니다.
─────────────────────────────────────────────────────────────────────────────────────────────────
"""

import os

# ────────────────────────────────────────────────────────────
# Moving Average 관련 상수
# ────────────────────────────────────────────────────────────
# • 단순 이동평균(SMA) 기간 리스트
#   - 환경변수 "SMA_WINDOWS"가 쉼표로 구분된 숫자로 제공되면 이를 사용하고,
#     그렇지 않으면 기본값 [5, 20, 60]을 사용합니다.
#   - 예: export SMA_WINDOWS="5,20,60"
_sma_env = os.getenv("SMA_WINDOWS")
if _sma_env:
    MOVING_AVERAGE_SMA_WINDOWS = [
        int(x) for x in _sma_env.split(",") if x.strip().isdigit()
    ]
else:
    MOVING_AVERAGE_SMA_WINDOWS = [5, 20, 60]
# 결과 예시: [5, 20, 60]  (단위: 일)

# • 지수 이동평균(EMA) 기간 리스트
#   - 환경변수 "EMA_WINDOWS"가 쉼표 구분 숫자로 제공되면 이를 사용, 아니면 기본값 [12, 26] 사용
#   - 예: export EMA_WINDOWS="12,26"
_ema_env = os.getenv("EMA_WINDOWS")
if _ema_env:
    MOVING_AVERAGE_EMA_WINDOWS = [
        int(x) for x in _ema_env.split(",") if x.strip().isdigit()
    ]
else:
    MOVING_AVERAGE_EMA_WINDOWS = [12, 26]
# 결과 예시: [12, 26]  (단위: 일)

# ────────────────────────────────────────────────────────────
# RSI(Relative Strength Index) 관련 상수
# ────────────────────────────────────────────────────────────
# • RSI 기본 기간 (일 단위)
#   - 환경변수 "RSI_PERIOD"가 있으면 사용, 없으면 기본값 14
#   - 예: export RSI_PERIOD="14"
RSI_DEFAULT_PERIOD = int(os.getenv("RSI_PERIOD", 14))

# ────────────────────────────────────────────────────────────
# MACD 관련 상수
# ────────────────────────────────────────────────────────────
# • MACD 계산 시 Fast EMA (짧은 기간)
#   - 환경변수 "MACD_FAST" 있으면 사용, 없으면 기본값 12
MACD_DEFAULT_FAST = int(os.getenv("MACD_FAST", 12))

# • MACD 계산 시 Slow EMA (긴 기간)
#   - 환경변수 "MACD_SLOW" 있으면 사용, 없으면 기본값 26
MACD_DEFAULT_SLOW = int(os.getenv("MACD_SLOW", 26))

# • MACD 신호선 EMA 기간
#   - 환경변수 "MACD_SIGNAL" 있으면 사용, 없으면 기본값 9
MACD_DEFAULT_SIGNAL = int(os.getenv("MACD_SIGNAL", 9))

# ────────────────────────────────────────────────────────────
# Bollinger Bands 관련 상수
# ────────────────────────────────────────────────────────────
# • Bollinger Band 중간선(SMA) 기간
#   - 환경변수 "BOLLINGER_WINDOW" 있으면 사용, 없으면 기본값 20
BOLLINGER_DEFAULT_WINDOW = int(os.getenv("BOLLINGER_WINDOW", 20))

# • 표준편차 배수 (Upper/Lower Band 계산 시 사용)
#   - 환경변수 "BOLLINGER_STD_DEV" 있으면 사용, 없으면 기본값 2
BOLLINGER_DEFAULT_STD_DEV = int(os.getenv("BOLLINGER_STD_DEV", 2))
