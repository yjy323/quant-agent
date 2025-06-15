# indicators/exceptions.py

"""
indicators 전용 예외 클래스를 정의합니다.
모든 Indicator 모듈에서 발생하는 예외는 이 클래스를 사용하도록 합니다.
"""


from typing import Optional


class IndicatorError(Exception):
    """
    • Indicator 계산 중 발생하는 예외의 기본 클래스입니다.
    • 단순히 메시지만 담아도 되지만, 필요하다면 'indicator_name' 같은 추가 속성으로
      어떤 지표에서 오류가 났는지 구분할 수 있습니다.
    """

    def __init__(self, message: str, indicator_name: Optional[str] = None):
        """
        :param message: 예외 설명 메시지
        :param indicator_name: (선택) 어떤 Indicator 클래스에서 발생했는지 이름
        """
        if indicator_name:
            full_msg = f"[{indicator_name}] {message}"
        else:
            full_msg = message
        super().__init__(full_msg)
        self.indicator_name = indicator_name
