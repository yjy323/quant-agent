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
        """기본 AI 지시사항"""
        return """
You are a Bitcoin investment expert.
Analyze the comprehensive market data and make investment decisions.

Consider:
1. Current investment status and portfolio balance
2. Technical indicators (RSI, MACD, Bollinger Bands, etc.)
3. Market trends from daily and hourly data
4. Orderbook pressure and liquidity
5. Risk management principles

Respond in JSON format:
{
    "decision": "buy|sell|hold",
    "reason": "detailed reasoning with technical analysis",
    "confidence": 85,
    "risk_level": "low|medium|high"
}
"""

    def format_data_for_ai(self, collected_data: dict) -> str:
        """AI 분석용 데이터 포맷팅"""
        # DataFrame을 JSON으로 변환
        daily_data = collected_data["market_data"]["daily_ohlcv"].to_json(
            orient="index", date_format="iso"
        )
        hourly_data = collected_data["market_data"]["hourly_ohlcv"].to_json(
            orient="index", date_format="iso"
        )

        formatted_data = {
            "investment_status": collected_data["investment_status"],
            "orderbook": collected_data["orderbook"],
            "daily_ohlcv_with_indicators": json.loads(daily_data),
            "hourly_ohlcv_with_indicators": json.loads(hourly_data),
            "analysis_timestamp": datetime.now().isoformat(),
        }

        return json.dumps(formatted_data, ensure_ascii=False, indent=2)

    def analyze(self, collected_data: dict) -> Any:
        """AI 분석 실행"""
        try:
            instructions = self.load_instructions()
            formatted_data = self.format_data_for_ai(collected_data)

            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": instructions}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": formatted_data}],
                    },
                ],
                text={"format": {"type": "json_object"}},
            )

            return json.loads(response.output_text)

        except Exception as e:
            print(f"AI 분석 오류: {e}")
            return {"decision": "hold", "reason": "Analysis failed", "confidence": 0}
