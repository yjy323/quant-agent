import os
import sys
from datetime import date

import streamlit as st
from services.db_service import DBService

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# 페이지 설정
st.set_page_config(
    page_title="자동매매 거래 내역 대시보드",
    layout="wide",
)

db_service = DBService()

# 사이드바: 조회 조건
st.sidebar.header("조회 설정")
limit = st.sidebar.slider("최근 N건 조회", min_value=1, max_value=500, value=50)
use_date_filter = st.sidebar.checkbox("기간 조회 사용", value=False)
if use_date_filter:
    col1, col2 = st.sidebar.columns(2)
    start_date = col1.date_input("시작일", value=date.today())
    end_date = col2.date_input("종료일", value=date.today())
else:
    start_date = end_date = None

if st.sidebar.button("🔄 데이터 새로고침"):
    st.experimental_rerun()

# 제목
st.title("📋 자동매매 거래 내역 대시보드")

# 데이터 로딩
if use_date_filter:
    df = db_service.get_records(limit=None, start_date=start_date, end_date=end_date)
else:
    df = db_service.get_records(limit=limit)

# 요약 메트릭
total_count = len(df)
success_rate = (df["trade_executed"].mean() * 100) if total_count else 0.0
avg_pl_rate = df["profit_loss_rate"].mean() if total_count else 0.0

latest_status = "N/A"
if total_count:
    latest = df.iloc[0]
    emoji = "✅" if latest["trade_executed"] else "❌"
    latest_status = f'{latest["ai_decision"].upper()} {emoji}'

c1, c2, c3, c4 = st.columns(4)
c1.metric("총 조회 건수", total_count)
c2.metric("체결 성공률", f"{success_rate:.2f}%")
c3.metric("평균 수익률", f"{avg_pl_rate:.2f}%")
c4.metric("최신 거래 상태", latest_status)

# 거래 내역 테이블
if not df.empty:
    display_df = df.loc[
        :,
        [
            "created_at",
            "ai_decision",
            "ai_ratio",
            "trade_executed",
            "profit_loss",
            "profit_loss_rate",
            "trade_order_id",
        ],
    ]
    display_df = display_df.rename(
        columns={
            "created_at": "시간",
            "ai_decision": "AI 결정",
            "ai_ratio": "비율(%)",
            "trade_executed": "체결 여부",
            "profit_loss": "손익(원)",
            "profit_loss_rate": "손익률(%)",
            "trade_order_id": "주문 ID",
        }
    )
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("조회된 거래 기록이 없습니다.")
