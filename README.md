# Quant-Agent: AI 기반 자동 매매 시스템

Quant-Agent는 Upbit 거래소의 차트 데이터, 뉴스, 자막, 차트 이미지를 멀티모달로 수집하고, 기술적 보조지표(MA, RSI, MACD, Bollinger Bands)와 LLM 분석(GPT-4.1-mini)을 결합하여 매수·매도·보류 결정을 자동으로 실행하는 AI 기반 자동 매매 시스템입니다.


## 1. 프로젝트 개요

* **목적**: 암호화폐 시장에서 시계열 수치 데이터와 멀티모달 입력(뉴스, YouTube 자막, 차트 이미지)을 종합 분석하여 보다 정교한 자동 매매를 실현
* **주요 기능**:

  * Upbit API를 통해 OHLCV(일봉/분봉) 데이터 수집
  * `youtube-transcript-api`로 YouTube 자막 수집 및 GPT 기반 감성·내용 분석
  * 뉴스 API(SerpAPI)로 최신 비트코인 뉴스 수집 및 LLM을 활용한 요약·감성 분석
  * Selenium/WebDriver로 차트 스크린샷 캡처 후 GPT-Vision 분석
  * `ta` 라이브러리의 기술적 지표(MA, RSI, MACD, Bollinger Bands) 계산 모듈화
  * 분석 결과를 바탕으로 `DecisionMaker`가 매수/매도/보류 판단
  * `Trader` 모듈이 Upbit 거래 API로 실제 주문 실행


## 2. 요구사항 (Prerequisites)
* **Python**: 3.11 (구성 파일 기준)
* **필수 라이브러리** (requirements.txt 참고)
* **환경 변수** (`.env`)

  * `OPENAI_API_KEY` : OpenAI API 키
  * `UPBIT_ACCESS_KEY`, `UPBIT_SECRET_KEY` : Upbit API Key/Secret
  * `SERPAPI_KEY` : 뉴스 수집(SerpAPI) API 키

## 3. 설치 방법 (Installation)

```bash
# 1) 저장소 클론
git clone https://github.com/yjy323/quant-agent.git quant-agent
cd quant-agent

# 2) 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 3) 의존성 설치
pip install -r requirements.txt

# 4) 환경 변수 설정
cp .env.example .env
# .env 파일에 각 키값을 입력
```

## 4. 설정 (Configuration)

* **config.py** (`src/config.py`)

  * `Config.TRADING_INTERVAL_SECONDS` : 매매 주기 (초)
  * `Config.MARKET` : 거래 심볼 (예: "KRW-BTC")
  * `Config.CHART_ANALYSIS_MODEL`, `Config.YOUTUBE_ANALYSIS_MODEL` 등 LLM 모델 설정
  * `Config.SQLITE_DB_PATH` 등 DB 경로 설정
* **.env**

  * `.env.example`에 정의된 변수와 동일

## 5. 아키텍처 (Architecture)

```
quant-agent/
├─ src/
│  ├─ main.py                   	# 워크플로우 Orchestrator
│  ├─ config.py                 	# 환경 및 설정 로딩
│  ├─ data_collector.py         	# OHLCV 수집 모듈
│  ├─ youtube_captions_collector.py	# YouTube 자막 수집 모듈
│  ├─ news_collector.py         	# 뉴스 수집 모듈
│  ├─ fear_greed_collector.py   	# Fear & Greed 수집 모듈
│  ├─ chart_image_collector.py  	# 차트 이미지 수집 모듈
│  ├─ database_manager.py       	# DB 저장 및 조회
│  ├─ decision_maker.py         	# LLM+지표 종합 판단
│  ├─ trader.py                 	# 거래 실행
│  └─ indicators/               	# 지표 계산 라이브러리
│     ├─ moving_average.py
│     ├─ rsi.py
│     ├─ macd.py
│     ├─ bollinger.py
│     └─ aggregator.py
├─ dashboard/                    	# Streamlit 기반 대시보드
│  └─ app.py
├─ tests/                        	# 단위 테스트
├─ scripts/                      	# 배포 스크립트
│  └─ deploy.sh
└─ .github/workflows/ci-cd.yml   	# CI/CD 파이프라인 설정
```

* **워크플로우**: 수집 → 저장 → 지표 계산 → LLM 분석 → 판단 → 거래
* **DB**: SQLite (`db/trading.db`), SQLite 사용

## 6. 테스트 (Tests)

* **단위 테스트**: `tests/` 폴더 내 각 모듈별 테스트 포함
* **테스트 실행**: `pytest -q`

## 7. 기여 가이드 (Contributing)

1. Fork 후 Github flows 전략에 따라 branch 생성
2. 코드 수정 및 커밋
   * 커밋 메시지는 `feat:`, `fix:`, `refactor:` 등 Angular JS Commit Conventions 준수
3. PR 생성
4. 코드 리뷰 및 병합


## 8. CI/CD Pipeline

프로젝트에는 이미 GitHub Actions 기반 CI/CD 파이프라인이 `.github/workflows/ci-cd.yml`에 정의되어 있습니다. 주요 단계:

1. **Pre-commit**: 코드 스타일 검사(black, isort, flake8) 및 타입 체크(mypy)
2. **Test**: pytest를 사용한 유닛 테스트 실행 (Pre-commit 성공 후)
3. **Deploy**: main 브랜치로의 Push 시 EC2 서버에 SSH 배포

   * **호스트**: `${{ secrets.EC2_HOST }}`
   * **SSH 키**: `${{ secrets.EC2_KEY }}`
   * **스크립트**: `bash scripts/deploy.sh`


## 10. 라이선스 (License)

본 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.
