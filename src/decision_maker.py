import json
from datetime import datetime
from typing import Any

from openai import OpenAI  # type: ignore

from config import Config


class DecisionMaker:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.AI_MODEL

    def load_instructions(self) -> str:
        """AI 지시사항 로드"""
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
        """개선된 AI 지시사항"""
        return """
You are a Bitcoin investment expert analyzing comprehensive market data and technical indicators.

## Available Data:
1. **Investment Status**: Current portfolio, balances, profit/loss
2. **Orderbook**: Market depth, bid/ask pressure
3. **Market Data**: Daily/Hourly OHLCV data
4. **Technical Indicators**:
   - Moving Averages (SMA/EMA): Trend direction and momentum
   - RSI: Momentum and overbought/oversold conditions
   - MACD: Trend changes and momentum shifts
   - Bollinger Bands: Volatility and price extremes

## Analysis Guidelines:
- **Trend Analysis**: Use moving averages and MACD for overall direction
- **Momentum**: RSI for entry/exit timing (oversold <30, overbought >70)
- **Volatility**: Bollinger Bands for volatility breakouts and mean reversion
- **Market Sentiment**: Orderbook for immediate supply/demand
- **Risk Management**: Consider position size and market conditions

## Decision Framework:
- **BUY**: Strong confluence of bullish signals across multiple indicators
- **SELL**: Strong confluence of bearish signals across multiple indicators
- **HOLD**: Mixed signals, insufficient conviction, or appropriate risk management

Synthesize all available data to make the most informed decision. Focus on confluence of signals rather than single indicators. Provide detailed reasoning that explains your technical analysis and decision logic.

Respond in JSON format:
{
    "decision": "buy|sell|hold",
    "reason": "detailed reasoning explaining your analysis and decision logic"
}
"""  # noqa: E501

    def format_data_for_ai(self, collected_data: dict) -> str:
        """AI 분석용 데이터 포맷팅 - 개선된 구조"""
        try:
            market_data = collected_data["market_data"]

            # OHLCV 데이터를 JSON으로 변환 (최근 5개만)
            daily_ohlcv = None
            hourly_ohlcv = None

            if market_data["daily_ohlcv"] is not None:
                daily_ohlcv = (
                    market_data["daily_ohlcv"]
                    .tail(5)
                    .to_json(orient="index", date_format="iso")
                )
                daily_ohlcv = json.loads(daily_ohlcv)

            if market_data["hourly_ohlcv"] is not None:
                hourly_ohlcv = (
                    market_data["hourly_ohlcv"]
                    .tail(5)
                    .to_json(orient="index", date_format="iso")
                )
                hourly_ohlcv = json.loads(hourly_ohlcv)

            formatted_data = {
                "analysis_timestamp": datetime.now().isoformat(),
                "investment_status": collected_data["investment_status"],
                "orderbook": collected_data["orderbook"],
                "market_data": {
                    "daily_ohlcv_recent": daily_ohlcv,
                    "hourly_ohlcv_recent": hourly_ohlcv,
                    "daily_indicators": market_data["daily_indicators"],
                    "hourly_indicators": market_data["hourly_indicators"],
                },
            }

            # 지표 요약 정보는 제거 - AI가 직접 원시 데이터를 분석하도록 함

            return json.dumps(formatted_data, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"데이터 포맷팅 오류: {e}")
            # 기본 구조라도 반환
            return json.dumps(
                {
                    "analysis_timestamp": datetime.now().isoformat(),
                    "investment_status": collected_data.get("investment_status", {}),
                    "orderbook": collected_data.get("orderbook", {}),
                    "error": f"데이터 포맷팅 중 오류 발생: {e}",
                },
                ensure_ascii=False,
                indent=2,
            )

    def analyze(self, collected_data: dict) -> Any:
        """AI 분석 실행"""
        try:
            instructions = self.load_instructions()
            formatted_data = self.format_data_for_ai(collected_data)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": instructions},
                    {
                        "role": "user",
                        "content": f"다음 데이터를 분석하여 투자 결정을 내려주세요:\n\n{formatted_data}",
                    },
                ],
                response_format={"type": "json_object"},
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"AI 분석 오류: {e}")
            return {"decision": "hold", "reason": f"AI 분석 실패로 인한 안전 보유: {e}"}
