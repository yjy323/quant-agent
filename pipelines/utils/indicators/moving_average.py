# indicators/moving_average.py

from typing import Any, Dict

import pandas as pd
from ta.trend import EMAIndicator, SMAIndicator

from .base import BaseIndicator
from .config import MOVING_AVERAGE_EMA_WINDOWS, MOVING_AVERAGE_SMA_WINDOWS
from .exceptions import IndicatorError


class MovingAverageIndicator(BaseIndicator):
    """
    ■ MovingAverageIndicator ■
    • SMA 및 EMA를 계산합니다.
    """

    def __init__(
        self,
        ohlcv_df: pd.DataFrame,
        sma_impl: type = SMAIndicator,
        ema_impl: type = EMAIndicator,
    ) -> None:
        super().__init__(ohlcv_df)
        self.close: pd.Series = self.ohlcv["close"]
        self._sma_impl = sma_impl
        self._ema_impl = ema_impl
        self.indicator_name = "MovingAverage"

    def _calculate_sma(self, full_series: bool = False) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        close_non_na = self.close.dropna()
        length = len(close_non_na)

        for window in MOVING_AVERAGE_SMA_WINDOWS:
            if length < window:
                raise IndicatorError(
                    message=f"데이터 개수({length}) < SMA 윈도우({window})",
                    indicator_name=self.indicator_name,
                )
            sma_series = self._sma_impl(close=self.close, window=window).sma_indicator()
            last_val = sma_series.iloc[-1]

            if pd.isna(last_val):
                raise IndicatorError(
                    message=f"SMA(window={window}) 결과가 NA입니다.",
                    indicator_name=self.indicator_name,
                )
            result[f"sma_{window}"] = float(last_val)

            if full_series:
                result[f"sma_{window}_series"] = sma_series

        return result

    def _calculate_ema(self, full_series: bool = False) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        close_non_na = self.close.dropna()
        length = len(close_non_na)

        for window in MOVING_AVERAGE_EMA_WINDOWS:
            if length < window:
                raise IndicatorError(
                    message=f"데이터 개수({length}) < EMA 윈도우({window})",
                    indicator_name=self.indicator_name,
                )
            ema_series = self._ema_impl(close=self.close, window=window).ema_indicator()
            last_val = ema_series.iloc[-1]

            if pd.isna(last_val):
                raise IndicatorError(
                    message=f"EMA(window={window}) 결과가 NA입니다.",
                    indicator_name=self.indicator_name,
                )
            result[f"ema_{window}"] = float(last_val)

            if full_series:
                result[f"ema_{window}_series"] = ema_series

        return result

    def calculate(self, full_series: bool = False) -> Dict[str, Any]:
        """
        • full_series=False (기본): SMA와 EMA의 마지막 값만 계산하여 반환
        • full_series=True : 전체 시계열도 함께 반환
        """
        sma_part = self._calculate_sma(full_series)
        ema_part = self._calculate_ema(full_series)

        combined: Dict[str, Any] = {}
        combined.update(sma_part)
        combined.update(ema_part)

        return {"moving_average": combined}
