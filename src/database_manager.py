# database_manager.py

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional

from config import Config


class DatabaseManager:
    def __init__(self) -> None:
        self.db_path = Config.SQLITE_DB_PATH
        self.table_name = Config.SQLITE_TABLE_NAME

        self.initialize_database()

    def initialize_database(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 테이블 생성
                cursor.execute(
                    f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_timestamp TEXT NOT NULL,

                    ai_decision TEXT NOT NULL CHECK(ai_decision IN ('buy', 'sell', 'hold')),
                    ai_ratio REAL NOT NULL DEFAULT 0.0,
                    ai_reason TEXT,

                    trade_executed BOOLEAN NOT NULL DEFAULT 0,
                    trade_order_id TEXT,
                    trade_result_json TEXT,

                    krw_balance REAL NOT NULL,
                    btc_balance REAL NOT NULL,
                    btc_current_price REAL NOT NULL,
                    btc_avg_buy_price REAL NOT NULL DEFAULT 0.0,
                    total_krw_value REAL NOT NULL,
                    profit_loss REAL NOT NULL DEFAULT 0.0,
                    profit_loss_rate REAL NOT NULL DEFAULT 0.0,

                    daily_sma_5 REAL,
                    daily_sma_20 REAL,
                    daily_sma_60 REAL,
                    daily_ema_12 REAL,
                    daily_ema_26 REAL,
                    daily_rsi REAL,
                    daily_macd_line REAL,
                    daily_macd_signal REAL,
                    daily_macd_histogram REAL,
                    daily_bollinger_upper REAL,
                    daily_bollinger_middle REAL,
                    daily_bollinger_lower REAL,
                    daily_bollinger_width REAL,

                    hourly_sma_5 REAL,
                    hourly_sma_20 REAL,
                    hourly_sma_60 REAL,
                    hourly_ema_12 REAL,
                    hourly_ema_26 REAL,
                    hourly_rsi REAL,
                    hourly_macd_line REAL,
                    hourly_macd_signal REAL,
                    hourly_macd_histogram REAL,
                    hourly_bollinger_upper REAL,
                    hourly_bollinger_middle REAL,
                    hourly_bollinger_lower REAL,
                    hourly_bollinger_width REAL,

                    orderbook_total_ask_size REAL,
                    orderbook_total_bid_size REAL,
                    orderbook_top5_json TEXT,

                    fear_greed_value INTEGER,
                    fear_greed_classification TEXT,
                    fear_greed_trend_direction TEXT,
                    fear_greed_trend_strength REAL,
                    fear_greed_avg_7d REAL,
                    fear_greed_consecutive_days INTEGER,

                    news_count INTEGER NOT NULL DEFAULT 0,
                    news_top3_titles TEXT,

                    chart_file_path TEXT,
                    chart_trend_direction TEXT,
                    chart_trading_signal TEXT,
                    chart_signal_strength INTEGER,
                    chart_key_patterns TEXT,
                    chart_analysis_summary TEXT,

                    youtube_overall_sentiment TEXT,
                    youtube_confidence INTEGER,
                    youtube_key_points TEXT,
                    youtube_analysis_summary TEXT,

                    data_collection_duration_ms INTEGER NOT NULL,
                    analysis_duration_ms INTEGER NOT NULL,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """  # noqa: E501
                )

                # 인덱스 생성
                cursor.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_cycle_timestamp "
                    f"ON {self.table_name}(cycle_timestamp)"
                )
                cursor.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_ai_decision "
                    f"ON {self.table_name}(ai_decision)"
                )
                cursor.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_trade_executed "
                    f"ON {self.table_name}(trade_executed)"
                )
                cursor.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_created_at "
                    f"ON {self.table_name}(created_at)"
                )

                conn.commit()
                print(f"✅ SQLite 데이터베이스 초기화 완료: {self.db_path}")

        except Exception as e:
            print(f"❌ 데이터베이스 초기화 실패: {e}")
            raise

    def record_trading_cycle(
        self,
        ai_decision: Dict[str, Any],
        ai_formatted_data: str,
        chart_result: Optional[Dict[str, Any]],
        youtube_data: Optional[Dict[str, Any]],
        trade_result: Optional[Any],
        cycle_start_time: datetime,
        analysis_duration_ms: int,
    ) -> bool:
        try:
            market_data = json.loads(ai_formatted_data)

            record = self._build_database_record(
                ai_decision=ai_decision,
                market_data=market_data,
                chart_result=chart_result,
                youtube_data=youtube_data,
                trade_result=trade_result,
                cycle_start_time=cycle_start_time,
                analysis_duration_ms=analysis_duration_ms,
            )

            self._insert_record(record)

            print("✅ 거래 사이클 데이터 DB 저장 완료")
            return True

        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"❌ DB 저장 실패: {e}")
            return False

    def _build_database_record(
        self,
        ai_decision: Dict[str, Any],
        market_data: Dict[str, Any],
        chart_result: Optional[Dict[str, Any]],
        youtube_data: Optional[Dict[str, Any]],
        trade_result: Optional[Any],
        cycle_start_time: datetime,
        analysis_duration_ms: int,
    ) -> Dict[str, Any]:
        record = {
            "cycle_timestamp": cycle_start_time.isoformat(),
            "analysis_duration_ms": analysis_duration_ms,
            "data_collection_duration_ms": 0,
        }

        record.update(self._extract_ai_decision(ai_decision))
        record.update(self._extract_trade_result(trade_result))
        record.update(self._extract_investment_status(market_data))
        record.update(self._extract_technical_indicators(market_data))
        record.update(self._extract_orderbook_data(market_data))
        record.update(self._extract_fear_greed_data(market_data))
        record.update(self._extract_news_data(market_data))
        record.update(self._extract_chart_analysis(chart_result))
        record.update(self._extract_youtube_analysis(youtube_data))

        return record

    def _extract_ai_decision(self, ai_decision: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ai_decision": ai_decision.get("decision", "hold"),
            "ai_ratio": float(ai_decision.get("ratio", 0.0)),
            "ai_reason": ai_decision.get("reason", ""),
        }

    def _extract_trade_result(self, trade_result: Optional[Any]) -> Dict[str, Any]:
        if trade_result is None:
            return {
                "trade_executed": False,
                "trade_order_id": None,
                "trade_result_json": None,
            }

        if isinstance(trade_result, dict):
            return {
                "trade_executed": True,
                "trade_order_id": trade_result.get("uuid", ""),
                "trade_result_json": json.dumps(trade_result, ensure_ascii=False),
            }

        return {
            "trade_executed": True,
            "trade_order_id": str(trade_result) if trade_result else "",
            "trade_result_json": json.dumps(
                {"result": str(trade_result)}, ensure_ascii=False
            ),
        }

    def _extract_investment_status(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        investment_status = market_data.get("investment_status", {})

        return {
            "krw_balance": float(investment_status.get("krw_balance", 0.0)),
            "btc_balance": float(investment_status.get("btc_balance", 0.0)),
            "btc_current_price": float(investment_status.get("btc_current_price", 0.0)),
            "btc_avg_buy_price": float(investment_status.get("btc_avg_buy_price", 0.0)),
            "total_krw_value": float(investment_status.get("total_krw_value", 0.0)),
            "profit_loss": float(investment_status.get("profit_loss", 0.0)),
            "profit_loss_rate": float(investment_status.get("profit_loss_rate", 0.0)),
        }

    def _extract_technical_indicators(
        self, market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        market_indicators = market_data.get("market_data", {})
        daily_indicators = market_indicators.get("daily_indicators", {})
        hourly_indicators = market_indicators.get("hourly_indicators", {})

        record = {}

        daily_ma = daily_indicators.get("moving_average", {})
        record.update(
            {
                "daily_sma_5": self._safe_float(daily_ma.get("sma_5")),
                "daily_sma_20": self._safe_float(daily_ma.get("sma_20")),
                "daily_sma_60": self._safe_float(daily_ma.get("sma_60")),
                "daily_ema_12": self._safe_float(daily_ma.get("ema_12")),
                "daily_ema_26": self._safe_float(daily_ma.get("ema_26")),
                "daily_rsi": self._safe_float(daily_indicators.get("rsi")),
            }
        )

        daily_macd = daily_indicators.get("macd", {})
        record.update(
            {
                "daily_macd_line": self._safe_float(daily_macd.get("macd_line")),
                "daily_macd_signal": self._safe_float(daily_macd.get("signal_line")),
                "daily_macd_histogram": self._safe_float(daily_macd.get("histogram")),
            }
        )

        daily_bollinger = daily_indicators.get("bollinger", {})
        record.update(
            {
                "daily_bollinger_upper": self._safe_float(
                    daily_bollinger.get("upper_band")
                ),
                "daily_bollinger_middle": self._safe_float(
                    daily_bollinger.get("middle_band")
                ),
                "daily_bollinger_lower": self._safe_float(
                    daily_bollinger.get("lower_band")
                ),
                "daily_bollinger_width": self._safe_float(
                    daily_bollinger.get("band_width")
                ),
            }
        )

        hourly_ma = hourly_indicators.get("moving_average", {})
        record.update(
            {
                "hourly_sma_5": self._safe_float(hourly_ma.get("sma_5")),
                "hourly_sma_20": self._safe_float(hourly_ma.get("sma_20")),
                "hourly_sma_60": self._safe_float(hourly_ma.get("sma_60")),
                "hourly_ema_12": self._safe_float(hourly_ma.get("ema_12")),
                "hourly_ema_26": self._safe_float(hourly_ma.get("ema_26")),
                "hourly_rsi": self._safe_float(hourly_indicators.get("rsi")),
            }
        )

        hourly_macd = hourly_indicators.get("macd", {})
        record.update(
            {
                "hourly_macd_line": self._safe_float(hourly_macd.get("macd_line")),
                "hourly_macd_signal": self._safe_float(hourly_macd.get("signal_line")),
                "hourly_macd_histogram": self._safe_float(hourly_macd.get("histogram")),
            }
        )

        hourly_bollinger = hourly_indicators.get("bollinger", {})
        record.update(
            {
                "hourly_bollinger_upper": self._safe_float(
                    hourly_bollinger.get("upper_band")
                ),
                "hourly_bollinger_middle": self._safe_float(
                    hourly_bollinger.get("middle_band")
                ),
                "hourly_bollinger_lower": self._safe_float(
                    hourly_bollinger.get("lower_band")
                ),
                "hourly_bollinger_width": self._safe_float(
                    hourly_bollinger.get("band_width")
                ),
            }
        )

        return record

    def _extract_orderbook_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        orderbook = market_data.get("orderbook", {})

        return {
            "orderbook_total_ask_size": self._safe_float(
                orderbook.get("total_ask_size")
            ),
            "orderbook_total_bid_size": self._safe_float(
                orderbook.get("total_bid_size")
            ),
            "orderbook_top5_json": json.dumps(
                orderbook.get("top_5_orderbook", []), ensure_ascii=False
            ),
        }

    def _extract_fear_greed_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        fear_greed = market_data.get("fear_greed_index", {})
        current_index = fear_greed.get("current_index", {})
        trend_analysis = fear_greed.get("trend_analysis", {})

        return {
            "fear_greed_value": self._safe_int(current_index.get("value")),
            "fear_greed_classification": current_index.get("classification", ""),
            "fear_greed_trend_direction": trend_analysis.get("trend_direction", ""),
            "fear_greed_trend_strength": self._safe_float(
                trend_analysis.get("trend_strength")
            ),
            "fear_greed_avg_7d": self._safe_float(trend_analysis.get("average_7d")),
            "fear_greed_consecutive_days": self._safe_int(
                trend_analysis.get("consecutive_days")
            ),
        }

    def _extract_news_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        news_analysis = market_data.get("news_analysis", {})
        news_articles = news_analysis.get("news_articles", [])

        top3_titles = [article.get("title", "") for article in news_articles[:3]]

        return {
            "news_count": int(news_analysis.get("final_count", 0)),
            "news_top3_titles": json.dumps(top3_titles, ensure_ascii=False),
        }

    def _extract_chart_analysis(
        self, chart_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not chart_result:
            return {
                "chart_file_path": None,
                "chart_trend_direction": None,
                "chart_trading_signal": None,
                "chart_signal_strength": None,
                "chart_key_patterns": None,
                "chart_analysis_summary": None,
            }

        return {
            "chart_file_path": chart_result.get("chart_file_path", ""),
            "chart_trend_direction": None,
            "chart_trading_signal": None,
            "chart_signal_strength": None,
            "chart_key_patterns": None,
            "chart_analysis_summary": None,
        }

    def _extract_youtube_analysis(
        self, youtube_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not youtube_data:
            return {
                "youtube_overall_sentiment": None,
                "youtube_confidence": None,
                "youtube_key_points": None,
                "youtube_analysis_summary": None,
            }

        return {
            "youtube_overall_sentiment": None,
            "youtube_confidence": None,
            "youtube_key_points": None,
            "youtube_analysis_summary": None,
        }

    def _safe_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _safe_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _insert_record(self, record: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            columns = list(record.keys())
            values = list(record.values())

            placeholders = ", ".join(["?" for _ in columns])
            column_names = ", ".join(columns)

            sql = f"INSERT INTO {self.table_name} ({column_names}) VALUES ({placeholders})"  # noqa: E501

            cursor.execute(sql, values)
            # The SQL and values are split for readability and to avoid long lines.
            conn.commit()

    def get_recent_records(self, limit: int = 10) -> list:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                )

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(f"❌ 레코드 조회 실패: {e}")
            return []

    def close(self) -> None:
        pass

    def _create_dummy_data(self) -> tuple:
        ai_decision = {
            "decision": "buy",
            "ratio": 25.5,
            "reason": "기술적 지표가 상승 신호를 보이며, 시장 심리가 개선되었습니다.",
        }

        ai_formatted_data = json.dumps(
            {
                "investment_status": {
                    "krw_balance": 1000000.0,
                    "btc_balance": 0.01234567,
                    "btc_current_price": 45000000.0,
                    "btc_avg_buy_price": 44000000.0,
                    "total_krw_value": 1555555.0,
                    "profit_loss": 55555.0,
                    "profit_loss_rate": 3.7,
                },
                "market_data": {
                    "daily_indicators": {
                        "moving_average": {
                            "sma_5": 44800000.0,
                            "sma_20": 44200000.0,
                            "sma_60": 43500000.0,
                            "ema_12": 44900000.0,
                            "ema_26": 44300000.0,
                        },
                        "rsi": {"rsi": 65.5},
                        "macd": {
                            "macd_line": 125000.0,
                            "signal_line": 110000.0,
                            "histogram": 15000.0,
                        },
                        "bollinger": {
                            "upper_band": 46000000.0,
                            "middle_band": 44500000.0,
                            "lower_band": 43000000.0,
                            "band_width": 3000000.0,
                        },
                    },
                    "hourly_indicators": {
                        "moving_average": {
                            "sma_5": 44850000.0,
                            "sma_20": 44250000.0,
                            "sma_60": 43550000.0,
                            "ema_12": 44950000.0,
                            "ema_26": 44350000.0,
                        },
                        "rsi": {"rsi": 68.2},
                        "macd": {
                            "macd_line": 135000.0,
                            "signal_line": 120000.0,
                            "histogram": 15000.0,
                        },
                        "bollinger": {
                            "upper_band": 46100000.0,
                            "middle_band": 44550000.0,
                            "lower_band": 43000000.0,
                            "band_width": 3100000.0,
                        },
                    },
                },
                "orderbook": {
                    "total_ask_size": 12.34567890,
                    "total_bid_size": 15.67890123,
                    "top_5_orderbook": [
                        {
                            "ask_price": 45001000,
                            "ask_size": 0.5,
                            "bid_price": 44999000,
                            "bid_size": 0.7,
                        },
                        {
                            "ask_price": 45002000,
                            "ask_size": 0.3,
                            "bid_price": 44998000,
                            "bid_size": 0.4,
                        },
                        {
                            "ask_price": 45003000,
                            "ask_size": 0.2,
                            "bid_price": 44997000,
                            "bid_size": 0.6,
                        },
                    ],
                },
                "fear_greed_index": {
                    "current_index": {"value": 72, "classification": "Greed"},
                    "trend_analysis": {
                        "trend_direction": "increasing",
                        "trend_strength": 8.5,
                        "average_7d": 68.3,
                        "consecutive_days": 3,
                    },
                },
                "news_analysis": {
                    "final_count": 5,
                    "news_articles": [
                        {"title": "Bitcoin Reaches New Monthly High"},
                        {"title": "Major Institution Adopts Bitcoin"},
                        {"title": "Regulatory Clarity Boosts Crypto Market"},
                    ],
                },
            },
            ensure_ascii=False,
        )

        chart_result = {
            "chart_file_path": "/path/to/dummy/chart.txt",
            "metadata": {"timestamp": datetime.now().isoformat(), "symbol": "KRW-BTC"},
        }

        youtube_data = {
            "videos": [
                {
                    "title": "Bitcoin Analysis 2025",
                    "channel": "Crypto Expert",
                    "has_transcript": True,
                }
            ]
        }

        trade_result = {
            "uuid": "dummy-trade-12345",
            "side": "bid",
            "market": "KRW-BTC",
            "volume": "0.00555555",
            "price": "45000000",
        }

        cycle_start_time = datetime.now()
        analysis_duration_ms = 1250

        return (
            ai_decision,
            ai_formatted_data,
            chart_result,
            youtube_data,
            trade_result,
            cycle_start_time,
            analysis_duration_ms,
        )

    def test_with_dummy_data(self) -> bool:
        print("🧪 더미 데이터로 DB 저장 테스트 시작...")

        try:
            dummy_data = self._create_dummy_data()

            success = self.record_trading_cycle(*dummy_data)

            if success:
                print("✅ 더미 데이터 저장 성공!")

                recent_records = self.get_recent_records(1)
                if recent_records:
                    record = recent_records[0]
                    print(f"📊 저장된 레코드 ID: {record['id']}")
                    print(
                        f"💰 AI 결정: {record['ai_decision']} ({record['ai_ratio']}%)"
                    )
                    print(f"🏦 KRW 잔고: {record['krw_balance']:,.0f}원")
                    print(f"₿  BTC 현재가: {record['btc_current_price']:,.0f}원")
                    print(f"📈 일봉 RSI: {record['daily_rsi']}")
                    print(
                        f"😨 공포탐욕지수: {record['fear_greed_value']} "
                        f"({record['fear_greed_classification']})"
                    )
                    print(f"📰 뉴스 개수: {record['news_count']}개")
                    return True
                else:
                    print("❌ 저장된 데이터 조회 실패")
                    return False
            else:
                print("❌ 더미 데이터 저장 실패")
                return False

        except Exception as e:
            print(f"❌ 더미 데이터 테스트 중 오류: {e}")
            return False


if __name__ == "__main__":
    print("🧪 DatabaseManager 테스트 모드")
    print("-" * 50)

    try:
        db_manager = DatabaseManager()

        test_success = db_manager.test_with_dummy_data()

        if test_success:
            print("\n📋 최근 저장된 레코드 3개:")
            print("-" * 50)
            records = db_manager.get_recent_records(3)

            for i, record in enumerate(records, 1):
                print(
                    f"{i}. ID: {record['id']} | "
                    f"결정: {record['ai_decision']} | "
                    f"시간: {record['created_at']} | "
                    f"거래실행: {'✅' if record['trade_executed'] else '❌'}"
                )

            print(f"\n✅ DatabaseManager 테스트 완료! DB 파일: {db_manager.db_path}")
        else:
            print("\n❌ 테스트 실패")

    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")

    print("-" * 50)
