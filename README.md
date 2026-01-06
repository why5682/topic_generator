# 💊 Pharmacoepidemiology Research Trend Generator

AI-powered tool that analyzes PubMed literature to identify research trends and generate novel hypothesis proposals for pharmacoepidemiology studies.

---

## 🌟 Features

- 🔍 **Real-time PubMed Search**: Fetches latest abstracts using NCBI Entrez API
- 🤖 **AI Analysis**: Uses Ollama LLM to analyze research trends
- 📊 **Gap Identification**: Automatically identifies evidence gaps in literature
- 💡 **Hypothesis Generation**: Proposes 3 novel research hypotheses with detailed methodology
- 📥 **Export Options**: Download reports in Markdown or Word (.docx) format
- ⚡ **Smart Caching**: SQLite-based cache for faster repeated queries

---

## 🚀 Quick Start (두 가지 방법)

### **방법 1: Streamlit Cloud (추천 - 설치 불필요)**

**클라우드 배포 버전 사용하기**
1. 배포된 앱 방문: [Your Streamlit Cloud URL]
2. 바로 사용 가능 (설치 필요 없음)

**직접 배포하기**
- 자세한 가이드: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- Git 업로드 체크리스트: [GIT_DEPLOYMENT_CHECKLIST.md](./GIT_DEPLOYMENT_CHECKLIST.md)

### **방법 2: 로컬 실행 (Windows - Docker)**

#### 1단계: 필수 프로그램 설치
1. **Docker Desktop** 설치 (필수)
   - [다운로드 링크](https://www.docker.com/products/docker-desktop/)
   - 설치 후 실행하여 초록색 바(Running)가 뜰 때까지 기다려 주세요

2. **Ollama** 설치 (선택 권장)
   - 클라우드 모델(gptoss-120b:cloud 등) 사용 시 필요
   - [다운로드 링크](https://ollama.com/download)
   - 설치 후 터미널에서 `ollama signin` 실행

#### 2단계: 실행
1. `run_app.bat` 파일을 더블 클릭
2. GPU 사용 여부 선택:
   - NVIDIA GPU 있음: `y` 입력
   - 없음: 엔터 (CPU 모드)
3. 브라우저가 자동으로 열림 (`http://localhost:8501`)

---

## 🔑 NCBI API Key 발급 방법

PubMed 검색을 위해 필수입니다:

1. [NCBI 계정 생성](https://www.ncbi.nlm.nih.gov/account/)
2. Settings → API Key Management
3. "Create an API Key" 클릭
4. 생성된 키를 `.env` 파일 또는 Streamlit Secrets에 추가

---

## 📦 프로젝트 구조

```
trend/
├── app.py                    # Streamlit 메인 앱
├── pubmed_client.py          # PubMed API 클라이언트 + 캐싱
├── analyzer.py               # LLM 기반 트렌드 분석
├── main.py                   # CLI 인터페이스 (옵션)
├── requirements.txt          # Python 의존성
├── .streamlit/
│   └── secrets.toml.example  # Secrets 템플릿
├── DEPLOYMENT_GUIDE.md       # 클라우드 배포 가이드
├── GIT_DEPLOYMENT_CHECKLIST.md  # Git 업로드 체크리스트
└── README.md                 # 이 파일
```

---

## ⚙️ 설정 변경

### **로컬 실행 시 (.env 파일)**
```env
ENTREZ_EMAIL=your_email@example.com
ENTREZ_API_KEY=your_ncbi_api_key
OLLAMA_MODEL=gptoss-120b:cloud
OLLAMA_HOST=http://localhost:11434
```

### **Streamlit Cloud 배포 시 (Secrets)**
Dashboard → Settings → Secrets에서 설정:
```toml
ENTREZ_EMAIL = "your_email@example.com"
ENTREZ_API_KEY = "your_ncbi_api_key"
OLLAMA_MODEL = "gptoss-120b:cloud"
OLLAMA_HOST = "https://your-ollama-endpoint.com"
```

---

## 📖 사용 예시

1. 연구 주제 입력 (예: "GLP-1 Agonists")
2. 분석할 논문 수 조정 (5-50개)
3. "🚀 Analyze Trends & Generate Hypotheses" 클릭
4. 결과 확인:
   - **Executive Summary**: 현재 연구 트렌드
   - **Evidence Gaps**: 문헌의 빈틈
   - **Hypotheses**: 3개의 새로운 연구 가설 + 방법론
5. Markdown 또는 Word 형식으로 다운로드

---

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **AI/LLM**: Ollama (customizable model)
- **Data Source**: NCBI PubMed (via Biopython Entrez)
- **Database**: SQLite (caching)
- **Export**: python-docx

---

## 🔒 보안 주의사항

- ❌ `.env` 파일을 Git에 업로드하지 마세요!
- ❌ 실제 `secrets.toml` 파일을 커밋하지 마세요!
- ✅ `.gitignore`가 민감한 파일을 보호하도록 설정됨
- ✅ Streamlit Cloud Secrets를 프로덕션 배포에 사용

---

## 🌐 Streamlit Cloud 배포

자세한 내용은 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 참조

**빠른 배포:**
1. GitHub에 푸시 ([GIT_DEPLOYMENT_CHECKLIST.md](./GIT_DEPLOYMENT_CHECKLIST.md) 참조)
2. [Streamlit Cloud](https://share.streamlit.io/) 연결
3. Dashboard에서 Secrets 설정
4. 배포 완료!

---

## 🎯 향후 개선 계획

- [ ] 다양한 LLM 제공사 지원 (OpenAI, Anthropic)
- [ ] 고급 필터링 옵션
- [ ] 인용 내보내기 (BibTeX, EndNote)
- [ ] 협업 기능
- [ ] 커스텀 프롬프트 템플릿

---

## 🆘 지원

- **문서**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md), [GIT_DEPLOYMENT_CHECKLIST.md](./GIT_DEPLOYMENT_CHECKLIST.md)
- **NCBI API 문서**: [링크](https://www.ncbi.nlm.nih.gov/books/NBK25500/)
- **Streamlit 문서**: [링크](https://docs.streamlit.io/)

---

**Built with ❤️ for Pharmacoepidemiology Research**
