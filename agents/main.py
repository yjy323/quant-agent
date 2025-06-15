from typing import Dict

from fastapi import FastAPI

from agents.routers.routers import router

app = FastAPI(
    title="Trading Bot API", description="비트코인 자동매매 봇 API", version="1.0.0"
)

app.include_router(router)


@app.get("/")  # type: ignore
def root() -> Dict[str, str]:
    return {"message": "Trading Bot API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
