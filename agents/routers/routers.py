from typing import Dict

from fastapi import APIRouter, HTTPException

from agents.services.scheduler import scheduler

router = APIRouter(prefix="/trading")


@router.post("/start")  # type: ignore
def start_trading() -> Dict[str, str]:
    """거래 봇 시작"""
    if scheduler.start():
        return {"status": "success", "message": "거래 봇이 시작되었습니다"}
    else:
        raise HTTPException(status_code=409, detail="거래 봇이 이미 실행 중입니다")


@router.post("/stop")  # type: ignore
def stop_trading() -> Dict[str, str]:
    """거래 봇 중단"""
    if scheduler.stop():
        return {"status": "success", "message": "거래 봇이 중단되었습니다"}
    else:
        raise HTTPException(status_code=400, detail="거래 봇이 실행 중이 아닙니다")
