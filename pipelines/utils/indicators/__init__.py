# indicators/__init__.py

"""
트레이딩 기술적 지표 모듈

사용법:
    from indicators import (
        MovingAverageIndicator,
        RSIIndicator,
        MACDIndicator,
        BollingerIndicator,
        IndicatorAggregator
    )

    # 또는
    from indicators.aggregator import IndicatorAggregator
    from indicators.rsi import RSIIndicator
"""

from .aggregator import IndicatorAggregator
from .base import BaseIndicator
from .bollinger import BollingerIndicator
from .exceptions import IndicatorError
from .macd import MACDIndicator
from .moving_average import MovingAverageIndicator
from .rsi import RSIIndicator

__all__ = [
    "BaseIndicator",
    "IndicatorError",
    "IndicatorAggregator",
    "MovingAverageIndicator",
    "RSIIndicator",
    "MACDIndicator",
    "BollingerIndicator",
]

__version__ = "1.0.0"
