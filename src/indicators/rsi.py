# indicators/rsi.py

from typing import Any, Dict

import pandas as pd
from ta.momentum import RSIIndicator

from .base import BaseIndicator
from .config import RSI_DEFAULT_PERIOD
from .exceptions import IndicatorError


class RSIIndicatorCustom(BaseIndicator):
    """
    ■ RSIIndicatorCustom ■
    • RSI(Relative Strength Index)를 계산합니다.
    • 기본 기간: config.RSI_DEFAULT_PERIOD (예: 14)
    • calculate(include_flags=False, full_series=False)
      - full_series=True 시 rsi_series 전체를 결과에 포함
    • 데이터 부족 또는 NA 결과 시 IndicatorError를 즉시 던집니다.
    """

    def __init__(
        self, ohlcv_df: pd.DataFrame, period: int = RSI_DEFAULT_PERIOD
    ) -> None:
        """
        :param ohlcv_df: 'open','high','low','close','volume' 컬럼이 모두 포함된,
                         타임스탬프 오름차순 정렬된 DataFrame
        :param period: RSI 계산 기간 (None이면 config.RSI_DEFAULT_PERIOD 사용)
        """
        super().__init__(ohlcv_df)
        self.close: pd.Series = self.ohlcv["close"]
        self.period: int = period
        self.indicator_name = "RSI"

    def calculate(self, full_series: bool = False) -> Dict[str, Any]:
        """
        • close 데이터에서 RSI를 계산하고 최신값을 반환합니다.
        • full_series=True 시 전체 rsi_series 포함
        • 데이터 부족 또는 결과 NA 시 IndicatorError를 즉시 던집니다.

        :param include_flags: bool, 과매수/과매도 플래그 포함 여부
        :param full_series: bool, RSI 전체 시리즈 포함 여부
        :return: Dict[str, Any], 예: {"rsi": float, ...}
        """
        close_non_na = self.close.dropna()
        length = len(close_non_na)

        if length < self.period:
            raise IndicatorError(
                message=f"데이터 개수({length}) < RSI 기간({self.period})",
                indicator_name=self.indicator_name,
            )

        rsi_obj = RSIIndicator(close=self.close, window=self.period)
        rsi_series = rsi_obj.rsi()
        last_val = rsi_series.iloc[-1]

        if pd.isna(last_val):
            raise IndicatorError(
                message=f"RSI(window={self.period}) 결과가 NA입니다.",
                indicator_name=self.indicator_name,
            )

        result: Dict[str, Any] = {"rsi": float(last_val)}

        if full_series:
            result["rsi_series"] = rsi_series

        return result
