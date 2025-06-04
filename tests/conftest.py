# conftest.py

import pandas as pd
import pytest


@pytest.fixture
def ohlcv_df():
    """
    정상적으로 SMA/EMA 윈도우(예: [5, 20, 60], EMA 윈도우도 충분히 커버) 계산이 가능하도록
    최소 60개 이상의 행을 가진 OHLCV DataFrame을 생성합니다.
    컬럼은 ['open', 'high', 'low', 'close', 'volume'] 을 반드시 포함해야 합니다.
    """

    # 간단하게 값이 연속 증가하도록 생성
    # open, high, low, close는 모두 1.0, 2.0, 3.0 ... 100.0 으로 설정
    # volume은 임의의 정수(여기서는 i*10)로 설정
    data = {
        "open": [float(i) for i in range(1, 101)],
        "high": [float(i + 0.5) for i in range(1, 101)],
        "low": [float(i - 0.5) for i in range(1, 101)],
        "close": [float(i) for i in range(1, 101)],
        "volume": [int(i * 10) for i in range(1, 101)],
    }

    df = pd.DataFrame(data)
    return df
