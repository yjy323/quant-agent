# tests/test_aggregator.py

from indicators.aggregator import IndicatorAggregator
from indicators.bollinger import BollingerIndicator
from indicators.macd import MACDIndicator
from indicators.moving_average import MovingAverageIndicator
from indicators.rsi import RSIIndicator


def test_aggregate_full_series_false(ohlcv_df):
    """
    full_series=False로 aggregate() 호출만 수행하고, 결과를 출력합니다.
    """
    ma = MovingAverageIndicator(ohlcv_df)
    rsi = RSIIndicator(ohlcv_df)
    macd = MACDIndicator(ohlcv_df)
    boll = BollingerIndicator(ohlcv_df)

    agg = IndicatorAggregator([ma, rsi, macd, boll])
    result = agg.aggregate(full_series=False)
    print("\n>> aggregate 결과(full_series=False):", result)

    assert result is not None
    assert "moving_average" in result
    assert "rsi" in result
    assert "macd" in result
    assert "bollinger" in result
