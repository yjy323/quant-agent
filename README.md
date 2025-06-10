# Quant Agent
> 비트코인 자동매매를 위한 AI 기반 퀀트 트레이딩 시스템

## 프로젝트 개요
Quant Agent는 암호화폐 시장 데이터를 수집하고 AI 분석을 통해 매매 결정을 내리는 자동화 봇입니다. 기술적 지표, 뉴스, 공포•탐욕 지수 등을 종합하여 투자 판단을 돕고, 실행 결과는 SQLite에 저장되며 Streamlit 대시보드로 시각화됩니다.

## 주요 기능
- 업비트 API를 이용한 시세 및 주문 정보 수집
- 이동평균, RSI, MACD, 볼린저밴드 등 기술적 지표 계산
- OpenAI 모델을 활용한 매수•매도 의사결정
- 실제 주문 실행 및 결과 기록
- 대시보드를 통한 거래 내역 조회
- GitHub Actions 기반 CI/CD 및 pre-commit 훅

## 설치 방법
1. 저장소 클론
   ```bash
   git clone <repository-url>
   cd quant-agent
   ```
2. 가상환경 생성 및 활성화
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

## 환경 변수 설정
프로그램 실행 전 `.env` 파일에 다음 값을 설정합니다. 예시는 `.env.example` 파일을 참고하세요.
- `OPENAI_API_KEY`
- `UPBIT_ACCESS_KEY`, `UPBIT_SECRET_KEY`
- `SERPAPI_KEY`

## 사용 방법
- 거래 봇 실행
  ```bash
  python src/main.py
  ```
- 대시보드 실행
  ```bash
  bash dashboard/run.sh
  ```

## 테스트 및 코드 품질 검사
pre-commit 훅과 pytest로 코드 품질을 확인할 수 있습니다.
```bash
pre-commit install
pre-commit run --all-files
pytest
```

## 폴더 구조
```text
quant-agent/
├── src/              # 핵심 파이썬 모듈
├── dashboard/        # Streamlit 대시보드
├── tests/            # pytest 테스트 코드
├── scripts/          # 배포 스크립트
├── requirements.txt  # 의존성 목록
└── README.md
```

## 기여 방법
1. 새로운 브랜치에서 기능을 개발합니다.
2. 커밋 메시지 템플릿을 지켜 주세요.
3. Pull Request 템플릿을 이용해 변경 사항을 설명합니다.

## 라이선스
본 프로젝트는 MIT 라이선스를 따릅니다.
