# decision_maker.py (Updated with YouTube Analysis)

import json
from typing import Any, Optional, cast

from openai import OpenAI  # type: ignore

from config import Config


class DecisionMaker:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.AI_MODEL
        self.chart_model = Config.CHART_ANALYSIS_MODEL
        self.youtube_model = Config.YOUTUBE_ANALYSIS_MODEL

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
You are a Bitcoin investment expert analyzing comprehensive market data, technical indicators, market sentiment, real-time chart images, and YouTube analyst opinions.

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
8. **YouTube Analysis**: Recent market sentiment from crypto analysts
   - overall_sentiment: Aggregated sentiment from YouTube videos (bullish/bearish/neutral)
   - confidence: Reliability score (1-10)
   - key_points: Important insights from recent analysis videos
   - summary: Concise overview of YouTube sentiment

## Decision Guidelines:
- **Primary factors**: Technical indicators and chart patterns (70% weight)
- **Supporting factors**: YouTube sentiment, news, fear/greed index (30% weight)
- Use YouTube analysis confidence score to weight its influence
- Higher confidence YouTube analysis should carry more decision weight
- Ignore YouTube analysis if confidence < 5

## Allocation Guidelines:
- **ratio**: Must be between 0-100
- **BUY decisions**: Percentage of available KRW to invest
- **SELL decisions**: Percentage of current BTC holdings to sell
- **HOLD decisions**: 0% allocation (no action required)

Respond in JSON format:
{
    "decision": "buy|sell|hold",
    "reason": "detailed reasoning combining technical analysis, chart patterns, and YouTube sentiment",
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

    def _analyze_youtube_captions(self, youtube_data: dict[str, Any]) -> dict[str, Any]:
        """YouTube captions analysis"""
        try:
            video = youtube_data.get("video", {})

            if (
                not video.get("has_transcript", False)
                or not video.get("transcript_text", "").strip()
            ):
                print("📺 No YouTube transcript available for analysis")
                return {
                    "overall_sentiment": "neutral",
                    "confidence": 0,
                    "key_points": [],
                    "summary": "No YouTube transcript available for analysis",
                }

            print("📺 Analyzing YouTube transcript...")

            transcript_text = video["transcript_text"][:5000]  # Limit length

            response = self.client.chat.completions.create(
                model=self.youtube_model,
                messages=[
                    {
                        "role": "user",
                        "content": f"""
Analyze the following YouTube Bitcoin/cryptocurrency analysis video transcript:

Channel: {video['channel']}
Title: {video['title']}

Transcript:
{transcript_text}

Based on this content, provide analysis on:

1. **Overall Market Sentiment**: bullish/bearish/neutral
2. **Confidence Score** (1-10): Based on analysis quality, specificity, and expertise
3. **Key Points** (3-5): Important investment insights, price predictions, technical analysis
4. **Summary**: One-line overview of the YouTube analysis

Respond in JSON format:
{{
    "overall_sentiment": "bullish|bearish|neutral",
    "confidence": 1-10,
    "key_points": ["point1", "point2", "point3"],
    "summary": "YouTube analysis summary"
}}
""",  # noqa: E501
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=Config.YOUTUBE_ANALYSIS_MAX_TOKENS,
            )

            result = cast(
                dict[str, Any], json.loads(response.choices[0].message.content)
            )

            # Validate and set defaults
            result["overall_sentiment"] = result.get("overall_sentiment", "neutral")
            result["confidence"] = max(0, min(10, result.get("confidence", 0)))
            result["key_points"] = result.get("key_points", [])[:5]
            result["summary"] = result.get("summary", "YouTube analysis completed")

            print(
                f"✅ YouTube analysis completed: {result['overall_sentiment']} (confidence: {result['confidence']}/10)"  # noqa: E501
            )
            return result

        except Exception as e:
            print(f"❌ YouTube analysis error: {e}")
            return {
                "overall_sentiment": "neutral",
                "confidence": 0,
                "key_points": [],
                "summary": "YouTube analysis failed",
            }

    def analyze(
        self,
        ai_formatted_data: str,
        chart_file_path: Optional[str] = None,
        youtube_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """수치 데이터, 차트 이미지, YouTube 자막을 통합 분석하여 투자 결정 수행"""
        instructions = self.load_instructions()

        # 1. 차트 이미지 분석 (있는 경우)
        chart_analysis = None
        if chart_file_path:
            print("📊 차트 이미지 분석 중...")
            chart_analysis = self._analyze_chart_image(chart_file_path)

        # 2. YouTube 자막 분석 (있는 경우)
        youtube_analysis = None
        if youtube_data:
            print("📺 YouTube 자막 분석 중...")
            youtube_analysis = self._analyze_youtube_captions(youtube_data)

        # 3. 통합 분석용 콘텐츠 구성
        content_parts = [
            {
                "type": "text",
                "text": f"""
Analyze the following comprehensive data to make a Bitcoin investment decision:

=== NUMERICAL DATA ===
{ai_formatted_data}

=== CHART ANALYSIS RESULTS ===
{json.dumps(chart_analysis, ensure_ascii=False, indent=2)
 if chart_analysis else "No chart analysis data available"}

=== YOUTUBE ANALYSIS RESULTS ===
{json.dumps(youtube_analysis, ensure_ascii=False, indent=2)
 if youtube_analysis else "No YouTube analysis data available"}

Make an optimal investment decision by comprehensively considering technical indicators, chart patterns, and YouTube sentiment.
Pay special attention to the YouTube analysis confidence score when weighting its influence on your decision.
""",  # noqa: E501
            }
        ]

        # 4. 최종 AI 분석 실행
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": content_parts},  # type: ignore[arg-type]
            ],
            response_format={"type": "json_object"},
        )

        result = cast(dict[str, Any], json.loads(response.choices[0].message.content))

        # 6. 분석 결과를 최종 결과에 포함
        if chart_analysis:
            result["chart_analysis"] = chart_analysis.get("summary", "차트 분석 완료")

        if youtube_analysis:
            result["youtube_analysis"] = youtube_analysis.get(
                "summary", "YouTube 분석 완료"
            )

        return result
