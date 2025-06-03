# indicators/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict

import pandas as pd

from .exceptions import IndicatorError


class BaseIndicator(ABC):
    """
    ┌────────────────────────────────────────────────────────────────────────────────────┐
    │  BaseIndicator                                                                  │
    │                                                                                │
    │  • 모든 보조지표(Indicator) 클래스가 상속받아야 하는 추상(base) 클래스입니다.    │
    │  • ohlcv_df: pandas.DataFrame 형태의 OHLCV 데이터 (필수 컬럼:                    │
    │    ['open','high','low','close','volume'])를 받습니다.                          │
    │  • 입력된 OHLCV DataFrame은 항상 타임스탬프 오름차순 정렬된 상태로 전달되어야 합니다.│
    │    내부에서는 인덱스를 재정렬하지 않습니다.                                   │
    │  • OHLCV 데이터는 Read-Only 용도로만 사용되므로, 얕은 참조(self.ohlcv = ohlcv_df)를 사용합니다. │
    │  • 하위 클래스는 calculate() 메서드를 반드시 구현해야 하며, 반환값이 Dict[str, Any] 형태여야 합니다. │
    └────────────────────────────────────────────────────────────────────────────────────┘
    """

    def __init__(self, ohlcv_df: pd.DataFrame) -> None:
        """
        :param ohlcv_df: 'open','high','low','close','volume' 컬럼을 반드시 포함하며,
                         타임스탬프 오름차순으로 정렬된 DataFrame
        """
        required_cols = {"open", "high", "low", "close", "volume"}
        if not required_cols.issubset(set(ohlcv_df.columns)):
            missing = required_cols.difference(set(ohlcv_df.columns))
            raise IndicatorError(
                f"OHLCV DataFrame에 필수 컬럼이 누락되었습니다: {missing}"
            )

        self.ohlcv: pd.DataFrame = ohlcv_df

    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """
        하위 클래스에서 반드시 구현해야 하는 메서드입니다.

        • 반환 타입: Dict[str, Any]
          예시) {"rsi": 45.2} 또는 {"moving_average": {"sma_5": 123.4, ...}}
        """
        raise NotImplementedError(
            "하위 클래스에서 calculate() 메서드를 구현해야 합니다."
        )
