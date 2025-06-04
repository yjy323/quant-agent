# tests/test_moving_average.py

from indicators.moving_average import MovingAverageIndicator


def test_moving_average_calculate(ohlcv_df):
    """
    calculate() 호출만 수행하고, 결과를 출력합니다.
    """
    indicator = MovingAverageIndicator(ohlcv_df)
    result = indicator.calculate(full_series=False)
    print("\n>> moving_average 결과(full_series=False):", result)

    assert result is not None


def test_moving_average_calculate_full_series(ohlcv_df):
    """
    calculate() 호출만 수행하고, 결과를 출력합니다.
    """
    indicator = MovingAverageIndicator(ohlcv_df)
    result = indicator.calculate(full_series=True)
    print("\n>> moving_average 결과(full_series=True):", result)

    assert result is not None
