# indicators/aggregator.py

from typing import Any, Dict, List

from .base import BaseIndicator
from .exceptions import IndicatorError


class IndicatorAggregator:
    """
    여러 Indicator 인스턴스를 받아서 각각 calculate(full_series=full_series) 결과를 한 딕셔너리로 합치는 클래스입니다.
    """

    def __init__(self, indicators: List[BaseIndicator]) -> None:
        """
        :param indicators: BaseIndicator를 상속받은 지표 인스턴스 리스트
        """
        for ind in indicators:
            if not isinstance(ind, BaseIndicator):
                raise IndicatorError(f"{ind!r}는 BaseIndicator를 상속해야 합니다.")
        self.indicators: List[BaseIndicator] = indicators

    def aggregate(self, full_series: bool = False) -> Dict[str, Any]:
        """
        각 Indicator의 calculate() 결과 dict들을 병합해 하나의 결과 dict로 반환합니다.
        첫 지표 오류 시 IndicatorError를 즉시 전파합니다.

        :param full_series: bool, 각 지표의 전체 시계열을 포함할지 여부
        :return: Dict[str, Any], 예:
            {
              "moving_average": {...},
              "rsi": {...},
              "macd": {...},
              "bollinger": {...}
            }
        """
        final_result: Dict[str, Any] = {}

        for indicator in self.indicators:
            single_result = indicator.calculate(full_series=full_series)
            if not isinstance(single_result, dict):
                raise IndicatorError(
                    f"{indicator.__class__.__name__}.calculate()는 dict를 반환해야 합니다."
                )

            final_result.update(single_result)

        return final_result
