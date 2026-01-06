# 📋 Git 배포 체크리스트

## ✅ Git에 올려야 하는 파일 (Required)

### **핵심 애플리케이션 파일**
- [ ] `app.py` ← **`app_cloud.py`를 복사해서 교체**
- [ ] `pubmed_client.py` ← **`pubmed_client_cloud.py`를 복사해서 교체**
- [ ] `analyzer.py` (그대로 사용)
- [ ] `main.py` (그대로 사용)
- [ ] `requirements.txt` ← **`requirements_cloud.txt`를 복사해서 교체**

### **설정 파일 (예제만!)**
- [ ] `.streamlit/secrets.toml.example` ← **예제 파일 (실제 secrets 아님!)**
- [ ] `.gitignore` ← **민감한 파일 보호**

### **문서**
- [ ] `DEPLOYMENT_GUIDE.md` ← **배포 가이드**
- [ ] `README.md` ← **프로젝트 설명 (옵션)**

---

## ❌ Git에 올리면 안 되는 파일 (DO NOT COMMIT!)

### **🔐 민감한 정보**
- [ ] `.env` ← **실제 API 키 포함!**
- [ ] `.streamlit/secrets.toml` ← **실제 시크릿!**

### **📦 로컬 개발 전용**
- [ ] `docker-compose.yml`
- [ ] `Dockerfile`
- [ ] `run_app.bat`
- [ ] `run_app.sh`

### **🗄️ 자동 생성 파일**
- [ ] `pubmed_cache.db` ← **캐시, 클라우드에서 재생성됨**
- [ ] `__pycache__/` ← **Python 캐시**
- [ ] `*.pyc`, `*.pyo`

### **백업/중복 파일**
- [ ] `app_cloud.py` ← **app.py로 복사 후 불필요**
- [ ] `pubmed_client_cloud.py` ← **pubmed_client.py로 복사 후 불필요**
- [ ] `requirements_cloud.txt` ← **requirements.txt로 복사 후 불필요**
- [ ] `*_local.py` (백업 파일)

---

## 🚀 단계별 실행 가이드

### **Step 1: 파일 교체 (중요!)**
```bash
cd c:\Users\User\Documents\우현\OneDrive\sandbox\trend

# 클라우드 버전으로 교체
copy app_cloud.py app.py
copy pubmed_client_cloud.py pubmed_client.py
copy requirements_cloud.txt requirements.txt
```

### **Step 2: Git 추적 상태 확인**
```bash
# 현재 Git 상태 확인
git status

# 추가될 파일 목록 미리보기
git add --dry-run .
```

### **Step 3: 필수 파일만 추가**
```bash
# .gitignore 먼저 추가 (중요!)
git add .gitignore

# 핵심 앱 파일 추가
git add app.py pubmed_client.py analyzer.py main.py requirements.txt

# 설정 파일 추가 (예제만)
git add .streamlit/secrets.toml.example

# 문서 추가
git add DEPLOYMENT_GUIDE.md GIT_DEPLOYMENT_CHECKLIST.md
```

### **Step 4: .env 파일이 추가 안 됐는지 재확인!**
```bash
# 추가될 파일 최종 확인
git status

# ⚠️ 만약 .env가 보이면 절대 커밋하지 마세요!
# 다음 명령으로 제거:
git reset .env
git reset .streamlit/secrets.toml
```

### **Step 5: 커밋 & 푸시**
```bash
# 커밋
git commit -m "🚀 Prepare app for Streamlit Cloud deployment"

# 푸시 (origin은 GitHub 리모트)
git push origin main
```

---

## 🔍 확인 사항

### **커밋 전 체크리스트**
- [ ] `.env` 파일이 **절대** 포함되지 않았는가?
- [ ] `secrets.toml` (실제 파일)이 포함되지 않았는가?
- [ ] `app.py`가 클라우드 버전으로 교체되었는가?
- [ ] `requirements.txt`에 `python-dotenv`가 **없는가**?
- [ ] `.gitignore`가 제대로 설정되었는가?

### **푸시 후 체크리스트**
- [ ] GitHub에서 `.env` 파일이 보이지 않는가?
- [ ] `app.py`가 `st.secrets` 사용하는 버전인가?
- [ ] README.md가 있어서 프로젝트 설명이 보이는가?

---

## 🆘 자주 하는 실수

### ❌ **실수 1: .env 파일을 커밋했어요!**
```bash
# 즉시 히스토리에서 제거
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 강제 푸시
git push origin --force --all
```
**더 나은 방법**: GitHub에서 repository deleted로 새로 만들기

### ❌ **실수 2: _cloud.py 파일을 그대로 올렸어요**
```bash
# 교체하기
copy app_cloud.py app.py
git add app.py
git commit -m "Fix: Use cloud version"
git push
```

### ❌ **실수 3: docker-compose.yml이 포함되었어요**
```bash
# 제거
git rm --cached docker-compose.yml
git commit -m "Remove local docker files"
git push
```

---

## 📁 최종 파일 구조 (Git에 올라가는 것)

```
trend/
├── .gitignore                      ✅ 필수
├── .streamlit/
│   └── secrets.toml.example        ✅ 예제만
├── app.py                          ✅ 클라우드 버전
├── pubmed_client.py                ✅ 클라우드 버전
├── analyzer.py                     ✅ 그대로
├── main.py                         ✅ 그대로
├── requirements.txt                ✅ 클라우드 버전
├── DEPLOYMENT_GUIDE.md             ✅ 가이드
├── GIT_DEPLOYMENT_CHECKLIST.md     ✅ 체크리스트
└── README.md                       🔷 옵션
```

**올라가면 안 되는 것:**
```
trend/
├── .env                            ❌ 절대 안됨!
├── .streamlit/secrets.toml         ❌ 절대 안됨!
├── pubmed_cache.db                 ❌ 캐시
├── docker-compose.yml              ❌ 로컬 전용
├── run_app.bat                     ❌ 로컬 전용
├── app_cloud.py                    ❌ 중복 (app.py로 복사됨)
├── pubmed_client_cloud.py          ❌ 중복
└── __pycache__/                    ❌ 자동 생성
```

---

## 💡 Pro Tips

1. **항상 .gitignore를 먼저 커밋하세요**
2. **민감한 정보는 Git 히스토리에 남으면 영구적입니다**
3. **`git add .` 대신 파일을 개별적으로 추가하세요**
4. **푸시 전에 `git status`로 2번 확인하세요**
5. **실제 secrets는 Streamlit Cloud 대시보드에서만 설정하세요**

---

궁금한 점이 있으면 언제든 물어보세요! 🚀
