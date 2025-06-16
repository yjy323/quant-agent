from typing import Dict

from fastapi import FastAPI

app = FastAPI(title="API Server", description="API Server", version="1.0.0")


@app.get("/")  # type: ignore
def root() -> Dict[str, str]:
    return {"message": "API Server is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
