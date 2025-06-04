# indicators/macd.py

from typing import Any, Dict

import pandas as pd
from ta.trend import MACD as _MACD

from .base import BaseIndicator
from .config import MACD_DEFAULT_FAST, MACD_DEFAULT_SIGNAL, MACD_DEFAULT_SLOW
from .exceptions import IndicatorError


class MACDIndicatorCustom(BaseIndicator):
    """
    ■ MACDIndicatorCustom ■
    • MACD(Moving Average Convergence Divergence)를 계산합니다.
    • 기본 fast, slow, signal 값은 config에 정의된 값을 사용합니다.
    • calculate(full_series=False)
      - full_series=True 시 macd_series, signal_series, histogram_series 포함
      - full_series=False 시 마지막 값만 포함
    • 데이터 부족 또는 계산 결과 NA 시 IndicatorError를 즉시 던집니다.
    """

    def __init__(
        self,
        ohlcv_df: pd.DataFrame,
        window_fast: int = MACD_DEFAULT_FAST,
        window_slow: int = MACD_DEFAULT_SLOW,
        window_sign: int = MACD_DEFAULT_SIGNAL,
    ) -> None:
        """
        :param ohlcv_df: 'open','high','low','close','volume' 컬럼을
                         타임스탬프 오름차순 정렬된 DataFrame
        :param window_fast: Fast EMA 기간
        :param window_slow: Slow EMA 기간
        :param window_sign: Signal EMA 기간
        """
        super().__init__(ohlcv_df)
        self.close: pd.Series = self.ohlcv["close"]
        self.window_fast: int = window_fast
        self.window_slow: int = window_slow
        self.window_sign: int = window_sign
        self.indicator_name = "MACD"

    def calculate(self, full_series: bool = False) -> Dict[str, Any]:
        """
        • MACD 라인, Signal 라인, Histogram을 계산합니다.
        • full_series=True 시 전체 시리즈도 포함하여 반환하고, False 시 마지막 값만 반환합니다.
        • 데이터 부족 또는 계산 결과 NA 시 IndicatorError를 즉시 던집니다.

        :param full_series: bool, 전체 시리즈를 결과에 포함할지 여부
        """
        close_non_na = self.close.dropna()
        length = len(close_non_na)
        min_required = max(self.window_fast, self.window_slow, self.window_sign)

        if length < min_required:
            raise IndicatorError(
                message=f"데이터 개수({length}) < MACD 최소 요구기간({min_required})",
                indicator_name=self.indicator_name,
            )

        macd_obj = _MACD(
            close=self.close,
            window_fast=self.window_fast,
            window_slow=self.window_slow,
            window_sign=self.window_sign,
        )
        macd_series = macd_obj.macd()
        signal_series = macd_obj.macd_signal()
        histogram_series = macd_obj.macd_diff()

        last_macd = macd_series.iloc[-1]
        last_signal = signal_series.iloc[-1]
        last_hist = histogram_series.iloc[-1]

        if pd.isna(last_macd) or pd.isna(last_signal) or pd.isna(last_hist):
            raise IndicatorError(
                message="MACD 구성 요소 중 NA가 존재합니다. 데이터 길이를 확인하세요.",
                indicator_name=self.indicator_name,
            )

        result: Dict[str, Any] = {
            "macd_line": float(last_macd),
            "signal_line": float(last_signal),
            "histogram": float(last_hist),
        }

        if full_series:
            result["macd_series"] = macd_series
            result["signal_series"] = signal_series
            result["histogram_series"] = histogram_series

        return {"macd": result}
