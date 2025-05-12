# RAG 챗봇 with Confluence & GitBook

이 프로젝트는 Confluence와 GitBook 지식 기반을 활용하는 RAG(Retrieval Augmented Generation) 챗봇입니다. Confluence 또는 GitBook에서 문서를 검색하고 관련 정보를 기반으로 질문에 답변합니다.

## 주요 기능

- Confluence 문서 자동 로드 및 처리
- GitBook 문서 자동 로드 및 처리 (sitemap 기반)
- 문서 분할 및 벡터 데이터베이스 저장
- OpenAI 모델을 사용한 질의응답
- Streamlit 기반 대화형 UI
- 소스 링크 참조 제공

## 업데이트 내역 (2024)

이 버전에서는 다음과 같은 개선사항이 적용되었습니다:

- **GitBook 지원 추가**: GitBook 문서를 sitemap을 통해 자동으로 로드하고 처리
- **문서 소스 선택 기능**: Confluence만, GitBook만, 또는 둘 다 사용하는 옵션 제공
- **토큰 초과 문제 해결**: 대용량 문서도 배치 처리를 통해 안정적으로 임베딩
- **최신 LangChain 패키지 사용**: langchain -> langchain-community, langchain-openai 등으로 업데이트
- **향상된 문서 분할**: 더 효율적인 문서 청킹으로 컨텍스트 유지 개선
- **개선된 UI/UX**: Streamlit UI 고급화 및 사용자 경험 향상
- **로깅 및 오류 처리**: 상세한 로깅으로 오류 추적 용이
- **성능 최적화**: 배치 처리 및 효율적인 임베딩으로 성능 향상

## 시스템 요구사항

- Python 3.9 이상
- OpenAI API 키
- Confluence API 접근 권한 (Confluence 사용 시)
- GitBook 사이트 접근 권한 (GitBook 사용 시)

## 설치 방법

1. 저장소를 클론합니다:
```
git clone https://github.com/yourusername/RAG-Chatbot-with-Confluence.git
cd RAG-Chatbot-with-Confluence
```

2. 가상환경을 생성하고 활성화합니다:
```
python -m venv venv
source venv/bin/activate  # Windows의 경우: venv\Scripts\activate
```

3. 필요한 패키지를 설치합니다:
```
pip install -r requirements.txt
```

4. `.env` 파일을 생성하고 다음 환경 변수를 설정합니다:
```
# 필수
OPENAI_API_KEY=your_openai_api_key

# Confluence 설정 (DOCUMENT_SOURCE가 confluence 또는 both인 경우 필요)
CONFLUENCE_SPACE_NAME=your_confluence_url
CONFLUENCE_SPACE_KEY=your_confluence_space_key
CONFLUENCE_PRIVATE_API_KEY=your_confluence_api_key
EMAIL_ADRESS=your_confluence_email

# GitBook 설정 (DOCUMENT_SOURCE가 gitbook 또는 both인 경우 필요)
GITBOOK_DOMAIN=https://docs.fe-ta.com
GITBOOK_SITEMAP=https://docs.fe-ta.com/sitemap-pages.xml

# 문서 소스 선택 (confluence, gitbook, both)
DOCUMENT_SOURCE=both
```

## 사용 방법

Streamlit 앱을 실행합니다:
```
streamlit run ./src/streamlit.py
```

브라우저에서 `http://localhost:8501`을 열어 챗봇을 사용할 수 있습니다.

## 프로젝트 구조

```
RAG-Chatbot-with-Confluence/
├── src/                   # 소스 코드
│   ├── load_db.py         # 데이터 로드 및 처리
│   ├── help_desk.py       # RAG 모델 구현
│   ├── streamlit.py       # Streamlit UI
│   ├── evaluate.py        # 모델 평가
│   └── main.py            # 메인 스크립트
├── db/                    # 벡터 데이터베이스 저장소
├── data/                  # 데이터 파일
├── docs/                  # 문서
├── config.py              # 설정 파일
├── requirements.txt       # 의존성 패키지
└── README.md              # 설명서
```

## 새로운 기능 설명

### GitBook 지원

GitBook 문서를 sitemap을 통해 자동으로 로드하고 처리할 수 있습니다. sitemap XML 파일에서 모든 URL을 추출하여 문서를 수집합니다.

### 문서 소스 선택 기능

환경 변수 `DOCUMENT_SOURCE`를 통해 어떤 문서 소스를 사용할지 선택할 수 있습니다:
- `confluence`: Confluence 문서만 사용
- `gitbook`: GitBook 문서만 사용
- `both`: Confluence와 GitBook 문서 모두 사용

### 배치 처리

새 버전에서는 OpenAI API의 토큰 제한을 초과하는 문제를 해결하기 위해 문서를 적절한 크기의 배치로 나누어 처리합니다. 이를 통해 대용량 문서도 안정적으로 임베딩할 수 있습니다.

### 개선된 UI

Streamlit 인터페이스가 개선되어 더 직관적이고 사용하기 쉬운 UI를 제공합니다. 사이드바와 스타일링이 추가되었으며, 챗 메시지 레이아웃이 최적화되었습니다.

### 로깅 및 오류 처리

상세한 로깅을 통해 시스템의 동작을 추적하고 문제를 진단할 수 있습니다. 각 단계에서 발생하는 오류를 자세히 기록하고 사용자에게 피드백을 제공합니다.

## 라이센스

이 프로젝트는 MIT 라이센스 하에 제공됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 기여 방법

1. 저장소를 포크합니다.
2. 새 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치를 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

## 문의 사항

문의사항이 있으시면 이슈를 생성하거나 이메일로 연락해주세요.