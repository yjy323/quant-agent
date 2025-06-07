# decision_maker.py

import json
from typing import Any, Optional, cast

from openai import OpenAI  # type: ignore

from config import Config


class DecisionMaker:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.AI_MODEL
        self.chart_model = Config.CHART_ANALYSIS_MODEL

    def load_instructions(self) -> str:
        try:
            with open(Config.INSTRUCTIONS_FILE, "r", encoding="utf-8") as file:
                return str(file.read())
        except FileNotFoundError:
            return str(self._get_default_instructions())
        except Exception as e:
            print(f"지시사항 파일 로드 오류: {e}")
            return str(self._get_default_instructions())

    def _get_default_instructions(self) -> str:
        return """
You are a Bitcoin investment expert analyzing comprehensive market data, technical indicators, market sentiment, and real-time chart images.

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
6. **News Analysis**: Real-time Bitcoin-related news
7. **Chart Image**: Real-time 1-minute candlestick chart for visual pattern analysis

## Allocation Guidelines:
- **ratio**: Must be between 0-100
- **BUY decisions**: Percentage of available KRW to invest
- **SELL decisions**: Percentage of current BTC holdings to sell
- **HOLD decisions**: 0% allocation (no action required)

Respond in JSON format:
{
    "decision": "buy|sell|hold",
    "reason": "detailed reasoning combining numerical analysis and chart pattern analysis",
    "ratio": 0-100
}
"""  # noqa: E501

    def _analyze_chart_image(self, chart_file_path: str) -> dict[str, Any]:
        """차트 이미지 전용 분석"""
        try:
            with open(chart_file_path, "r", encoding="utf-8") as f:
                chart_base64 = f.read()

            response = self.client.chat.completions.create(
                model=self.chart_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """
Analyze this Bitcoin 1-minute candlestick chart and provide insights on:

1. **Candlestick Patterns**: Identify any significant patterns (doji, hammer, engulfing, etc.)
2. **Trend Analysis**: Current trend direction and strength
3. **Support/Resistance**: Key price levels visible on the chart
4. **Volume Analysis**: Price-volume relationship patterns
5. **Chart Formations**: Any emerging patterns (triangles, flags, etc.)
6. **Trading Signals**: Visual buy/sell signals from chart patterns

Respond in JSON format:
{
    "trend_direction": "bullish|bearish|sideways",
    "key_patterns": ["list of identified patterns"],
    "support_levels": [price levels],
    "resistance_levels": [price levels],
    "volume_insight": "description of volume patterns",
    "trading_signal": "buy|sell|hold",
    "signal_strength": 1-10,
    "summary": "concise chart analysis summary"
}
""",  # noqa: E501
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{chart_base64}"
                                },
                            },
                        ],
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=Config.CHART_ANALYSIS_MAX_TOKENS,
            )

            return cast(dict[str, Any], json.loads(response.choices[0].message.content))

        except Exception as e:
            print(f"차트 이미지 분석 오류: {e}")
            return {
                "trend_direction": "unknown",
                "key_patterns": [],
                "support_levels": [],
                "resistance_levels": [],
                "volume_insight": "분석 실패",
                "trading_signal": "hold",
                "signal_strength": 0,
                "summary": "차트 분석을 수행할 수 없습니다",
            }

    def analyze(
        self, ai_formatted_data: str, chart_file_path: Optional[str] = None
    ) -> dict[str, Any]:
        """수치 데이터와 차트 이미지를 통합 분석하여 투자 결정 수행"""
        instructions = self.load_instructions()

        chart_analysis = None
        if chart_file_path:
            print("📊 차트 이미지 분석 중...")
            chart_analysis = self._analyze_chart_image(chart_file_path)

        content_parts = [
            {
                "type": "text",
                "text": f"""
다음 종합 데이터를 분석하여 비트코인 투자 결정을 내려주세요:

=== 수치 데이터 ===
{ai_formatted_data}

=== 차트 분석 결과 ===
{json.dumps(chart_analysis, ensure_ascii=False, indent=2)
 if chart_analysis else "차트 분석 데이터 없음"}

수치적 지표와 차트 패턴을 종합적으로 고려하여 최적의 투자 판단을 내려주세요.
""",
            }
        ]

        if chart_file_path:
            try:
                with open(chart_file_path, "r", encoding="utf-8") as f:
                    chart_base64 = f.read()

                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{chart_base64}"
                        },  # type: ignore
                    }
                )
            except Exception as e:
                print(f"차트 이미지 로드 오류: {e}")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": content_parts},  # type: ignore[arg-type]
            ],
            response_format={"type": "json_object"},
        )

        result = cast(dict[str, Any], json.loads(response.choices[0].message.content))

        if chart_analysis:
            result["chart_analysis"] = chart_analysis["summary"]

        return result
