# 배포 가이드 - GitHub 자동 배포

이 문서는 GitHub와 연동하여 자동으로 배포하는 방법을 설명합니다.

## 🚀 Render로 자동 배포 (추천)

Render는 GitHub와 연동하여 코드를 푸시할 때마다 자동으로 배포됩니다.

### 1단계: Render 계정 생성

1. [Render.com](https://render.com) 접속
2. **"Get Started for Free"** 클릭
3. **GitHub 계정으로 로그인**

### 2단계: 새 Web Service 생성

1. 대시보드에서 **"New +"** 버튼 클릭
2. **"Web Service"** 선택
3. **"Connect a repository"** 에서 GitHub 연결

### 3단계: 저장소 선택

1. GitHub 저장소 목록에서 **`liveq/notebook`** 찾기
2. 만약 안 보이면 **"Configure account"** 클릭하여 권한 부여
3. **"Connect"** 버튼 클릭

### 4단계: 배포 설정

다음과 같이 설정:

```
Name: notebook-lte-search (또는 원하는 이름)
Region: Singapore (가장 가까운 지역 선택)
Branch: claude/save-missing-code-011CUeSJXKciYKGzKiWPBLd6
Root Directory: (비워두기)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
Instance Type: Free
```

### 5단계: 환경 변수 설정 (선택사항)

"Advanced" 섹션에서:
- `FLASK_ENV` = `production`
- `PYTHON_VERSION` = `3.11.0`

### 6단계: 배포 시작

1. **"Create Web Service"** 버튼 클릭
2. 자동으로 배포가 시작됩니다 (5-10분 소요)
3. 배포 로그를 실시간으로 확인 가능

### 7단계: 접속

배포가 완료되면 URL이 표시됩니다:
```
https://notebook-lte-search.onrender.com
```

이 URL로 **어디서든 접속 가능**합니다! 🎉

---

## 🔄 자동 배포 작동 방식

이제 GitHub에 코드를 푸시하면:

```bash
git add .
git commit -m "업데이트"
git push
```

→ Render가 자동으로 감지하고 재배포합니다!

---

## 📱 사용 방법

### 데스크탑에서
```
https://[your-app-name].onrender.com
```

### 스마트폰에서
1. 위 URL을 모바일 브라우저에 입력
2. 즐겨찾기에 추가
3. 언제든 접속!

---

## 💡 다른 배포 옵션

### Railway (GitHub 자동 배포)

1. [Railway.app](https://railway.app) 접속
2. GitHub 연동
3. 저장소 선택
4. 자동 배포 완료

### Fly.io (GitHub Actions)

```bash
# Fly CLI 설치
curl -L https://fly.io/install.sh | sh

# 로그인
fly auth login

# 앱 생성 및 배포
fly launch
fly deploy
```

### Heroku (GitHub 자동 배포)

1. [Heroku.com](https://heroku.com) 가입
2. 새 앱 생성
3. Deploy 탭 → GitHub 연동
4. Automatic deploys 활성화

---

## ⚠️ 무료 플랜 제한사항

### Render 무료 플랜
- ✅ 자동 배포
- ✅ HTTPS 지원
- ⚠️ 15분 비활성 시 슬립 모드 (첫 접속 시 깨어나는데 30초 소요)
- ⚠️ 월 750시간 제한

### 해결 방법
- **UptimeRobot** 같은 서비스로 주기적으로 핑 보내기
- 또는 유료 플랜 사용 ($7/월)

---

## 🔧 문제 해결

### 배포 실패 시
1. Render 로그 확인
2. requirements.txt 파일 확인
3. Python 버전 확인

### 슬립 모드 해제
- 첫 접속 시 30초 정도 기다리면 활성화됩니다
- 이후 15분간 활성 상태 유지

### 크롤링이 작동하지 않는 경우
- 대상 사이트들이 서버 IP를 차단할 수 있음
- 로그인이 필요한 사이트는 추가 설정 필요

---

## 📞 지원

문제가 발생하면:
- GitHub Issues: https://github.com/liveq/notebook/issues
- Render 문서: https://render.com/docs

---

## 🎉 완료!

이제 다음이 가능합니다:
- ✅ GitHub에 푸시 → 자동 배포
- ✅ 인터넷 어디서나 접속
- ✅ 스마트폰/태블릿/PC 모두 사용 가능
- ✅ 친구와 URL 공유 가능

**축하합니다! 웹 서비스가 배포되었습니다!** 🚀
