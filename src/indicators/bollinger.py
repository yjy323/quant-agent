# indicators/bollinger.py

from typing import Any, Dict

import pandas as pd
from ta.volatility import BollingerBands as _BollingerBands

from .base import BaseIndicator
from .config import BOLLINGER_DEFAULT_STD_DEV, BOLLINGER_DEFAULT_WINDOW
from .exceptions import IndicatorError


class BollingerIndicator(BaseIndicator):
    """
    ■ BollingerIndicator ■
    • 볼린저 밴드(Bollinger Bands)를 계산하고, 항상 전체 시계열, 최신값, 밴드 폭을 함께 반환합니다.
    """

    def __init__(
        self,
        ohlcv_df: pd.DataFrame,
        window: int = BOLLINGER_DEFAULT_WINDOW,
        window_dev: int = BOLLINGER_DEFAULT_STD_DEV,
    ) -> None:
        """
        :param ohlcv_df: 'open','high','low','close','volume' 컬럼을
                         타임스탬프 오름차순 정렬된 DataFrame
        :param window: 중간선(SMA) 기간
        :param window_dev: 표준편차 배수
        """
        super().__init__(ohlcv_df)
        self.close: pd.Series = self.ohlcv["close"]
        self.window: int = window
        self.window_dev: int = window_dev
        self.indicator_name = "Bollinger"

    def calculate(self, full_series: bool = False) -> Dict[str, Any]:
        """
        • close 데이터에서 Bollinger Band 상단, 중단, 하단을 계산합니다.
        • full_series=True 시 upper_series, middle_series, lower_series도 포함
        • 데이터 부족 또는 계산 결과 NA 시 IndicatorError를 즉시 던집니다.
        """
        close_non_na = self.close.dropna()
        length = len(close_non_na)

        if length < self.window:
            raise IndicatorError(
                message=f"데이터 개수({length}) < Bollinger 윈도우({self.window})",
                indicator_name=self.indicator_name,
            )

        bb_obj = _BollingerBands(
            close=self.close, window=self.window, window_dev=self.window_dev
        )
        upper_series = bb_obj.bollinger_hband()
        middle_series = bb_obj.bollinger_mavg()
        lower_series = bb_obj.bollinger_lband()

        last_upper = upper_series.iloc[-1]
        last_middle = middle_series.iloc[-1]
        last_lower = lower_series.iloc[-1]

        if pd.isna(last_upper) or pd.isna(last_middle) or pd.isna(last_lower):
            raise IndicatorError(
                message="Bollinger Band 계산 결과 중 NA가 존재합니다. 데이터 길이를 확인하세요.",
                indicator_name=self.indicator_name,
            )

        band_width = float(last_upper - last_lower)

        result: Dict[str, Any] = {
            "upper_band": float(last_upper),
            "middle_band": float(last_middle),
            "lower_band": float(last_lower),
            "band_width": band_width,
        }

        if full_series:
            result["upper_series"] = upper_series
            result["middle_series"] = middle_series
            result["lower_series"] = lower_series

        return {"bollinger": result}
