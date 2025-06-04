# tests/test_bollinger.py

from indicators.bollinger import BollingerIndicator


def test_bollinger_calculate(ohlcv_df):
    """
    calculate() 호출만 수행하고, 결과를 출력합니다.
    기본 옵션(full_series=False)으로 실행합니다.
    """
    indicator = BollingerIndicator(ohlcv_df)
    result = indicator.calculate(full_series=False)
    print("\n>> bollinger 결과(full_series=False):", result)

    assert result is not None


def test_bollinger_calculate_full_series(ohlcv_df):
    """
    calculate() 호출만 수행하고, 결과를 출력합니다.
    full_series=True 옵션으로 실행합니다.
    """
    indicator = BollingerIndicator(ohlcv_df)
    result = indicator.calculate(full_series=True)
    print("\n>> bollinger 결과(full_series=True):", result)

    assert result is not None
