# Quant Agent
> 퀀트 투자를 위한 AI Agent 시스템 개발 프로젝트

## 📚 프로젝트 소개

quant-agent는 퀀트 투자 전략을 자동화하고, AI 기반 의사결정을 지원하는 투자 에이전트 시스템입니다.

## 📦 코드 관리

- **Git Commit 메시지 템플릿**: 일관된 커밋 메시지 작성을 위해 템플릿을 제공합니다.
- **Git PR 템플릿**: 효과적인 코드 리뷰를 위한 Pull Request 템플릿이 준비되어 있습니다.

## 🛠️ 개발 환경

- **코드 포매터 & 린트**: 코드 품질 유지를 위해 포매터와 린트 도구를 설정했습니다. (예: black, isort, flake8 등)
- **가상환경 & 패키지 관리**: `requirements.txt`를 통해 필요한 패키지를 관리하며, Python 가상환경(venv, conda 등) 사용을 권장합니다.
- **pre-commit**: 주요 코드 스타일 및 린트 체크를 커밋 전에 자동으로 수행합니다.

## 🚀 실행 환경

1. Python 가상환경 생성 및 활성화
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```
3. 환경 변수 설정
   `.env` 파일을 참고하여 필요한 환경변수를 설정하세요. 예시는 `.env.example`에 있습니다.

## 🛫 배포 및 CI/CD

- **CI/CD 워크플로우**: Github Actions 기반의 자동화된 테스트 및 배포 파이프라인을 제공합니다. `.github/workflows/ci-cd.yml` 파일을 참고하세요.
- **pre-commit**: 커밋 시 자동으로 코드 스타일 및 린트 검사를 수행합니다.

## 💡 기여 가이드

1. 새로운 기능을 개발하거나 버그를 수정할 때는 브랜치를 분리하여 작업하세요.
2. 커밋 메시지 및 PR 템플릿을 준수해 주세요.
3. 코드 변경 전, 반드시 린트/포매터 및 pre-commit 훅을 통과해야 합니다.

## 📂 주요 파일 구조

```
quant-agent/
├── .github/           # Github 관련 템플릿 및 워크플로우
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── ...
├── requirements.txt   # Python 패키지 목록
├── .env.example       # 환경 변수 예시 파일
├── .gitignore         # Git 무시 파일
└── ...
```


## 📝 라이선스

본 프로젝트는 MIT 라이선스를 따릅니다.

