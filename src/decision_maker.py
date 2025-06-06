# decision_maker.py

import json
from typing import Any, cast

from openai import OpenAI  # type: ignore

from config import Config


class DecisionMaker:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.AI_MODEL

    def load_instructions(self) -> str:
        try:
            # type: ignore[attr-defined]
            with open(Config.INSTRUCTIONS_FILE, "r", encoding="utf-8") as file:
                return str(file.read())
        except FileNotFoundError:
            return str(self._get_default_instructions())
        except Exception as e:
            print(f"지시사항 파일 로드 오류: {e}")
            return str(self._get_default_instructions())

    def _get_default_instructions(self) -> str:
        return """
You are a Bitcoin investment expert analyzing comprehensive market data, technical indicators, and market sentiment.

## Available Data:
1. **Investment Status**: Current portfolio, balances, profit/loss
2. **Orderbook**: Market depth, bid/ask pressure, immediate supply/demand
3. **Market Data**: Daily/Hourly OHLCV data with technical indicators
4. **Technical Indicators**:
   - Moving Averages (SMA/EMA): Trend direction and momentum
   - RSI: Momentum and overbought/oversold conditions (oversold <30, overbought >70)
   - MACD: Trend changes and momentum shifts
   - Bollinger Bands: Volatility and price extremes
5. **Fear & Greed Index**: Market sentiment and psychological analysis
   - Current sentiment state and 7-day trend
   - Contrarian investment opportunities
   - Market psychology and crowd behavior
6. **News Analysis**: Real-time Bitcoin-related news
   - Top 5 recent news articles with titles, snippets, sources
   - Market context and news relevance assessment
   - News impact on short-term and medium-term price movements
   - Regulatory updates, institutional adoption, technical developments

## Allocation Guidelines:
- **ratio**: Must be between 0-100
- **BUY decisions**: Percentage of available KRW to invest
- **SELL decisions**: Percentage of current BTC holdings to sell
- **HOLD decisions**: 0% allocation (no action required)
- Consider current portfolio balance and risk management

Provide detailed reasoning that explains both technical analysis, sentiment interpretation, and position sizing logic.

Respond in JSON format:
{
    "decision": "buy|sell|hold",
    "reason": "detailed reasoning explaining technical analysis, sentiment analysis, and position sizing logic",
    "ratio": 0-100
}
"""  # noqa: E501

    def analyze(self, ai_formatted_data: str) -> dict[str, Any]:
        """
        AI 분석 실행 (포맷팅된 데이터 문자열 받음)

        Args:
            ai_formatted_data: CryptoDataCollector에서 포맷팅된 JSON 문자열

        Returns:
            dict: AI 분석 결과 {decision, reason, ratio}
        """
        instructions = self.load_instructions()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {
                    "role": "user",
                    "content": f"다음 데이터를 분석하여 투자 결정을 내려주세요. "
                    f"기술적 지표와 공포탐욕지수를 종합적으로 고려하세요:\n\n{ai_formatted_data}",
                },
            ],
            response_format={"type": "json_object"},
        )

        return cast(dict[str, Any], json.loads(response.choices[0].message.content))
