from datetime import date

import pandas as pd

from database_manager import DatabaseManager


class DBService:
    def __init__(self) -> None:
        self.manager = DatabaseManager()

    def get_records(
        self,
        limit: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        """
        DB에서 거래 기록을 조회하고 DataFrame으로 반환합니다.
        - limit 지정 시 최근 N건만 가져옵니다.
        - start_date/end_date 지정 시 해당 기간 필터링합니다.
        """
        # 1) 원본 레코드 조회
        if limit is not None:
            records = self.manager.get_recent_records(limit)
        else:
            # limit 미지정 시, 충분히 큰 수로 전체 조회
            records = self.manager.get_recent_records(10_000)

        df = pd.DataFrame(records)

        if df.empty:
            return df

        # 2) 문자열 → datetime
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])

        # 3) 기간 필터링
        if start_date is not None:
            df = df[df["created_at"].dt.date >= start_date]
        if end_date is not None:
            df = df[df["created_at"].dt.date <= end_date]

        # 4) 최신 순 정렬
        if "created_at" in df.columns:
            df = df.sort_values("created_at", ascending=False).reset_index(drop=True)

        return df
