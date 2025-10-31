# 중고 노트북 LTE 매물 검색 (React + GitHub Pages)

![Deploy](https://github.com/liveq/notebook/actions/workflows/crawl-and-deploy.yml/badge.svg)

**순수 GitHub만 사용! 서버 없음! 완전 무료!**

중고나라, 번개장터, 당근마켓에서 LTE 탑재 2-in-1 노트북을 자동 검색하여 React 웹앱으로 보여줍니다.

## 🚀 배포된 앱

**지금 바로 사용:**
```
https://liveq.github.io/notebook/
```

## ✨ 특징

- ✅ **서버 없음** - 순수 정적 사이트 (GitHub Pages)
- ✅ **자동 크롤링** - 매일 자동 실행 (GitHub Actions)
- ✅ **React** - 모던한 UI/UX
- ✅ **반응형** - 모바일 & 데스크탑 완벽 지원
- ✅ **무료** - GitHub만 사용, 비용 $0

## 🏗️ 작동 방식

```
┌─────────────────────────────────────────────┐
│  GitHub Actions (매일 자동 실행)             │
│  1. Python 크롤링 → data/results.json      │
│  2. React 앱 빌드 → dist/                  │
│  3. GitHub Pages 배포                       │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│  사용자가 접속                               │
│  → React 앱 로드                            │
│  → results.json 읽기                        │
│  → 매물 표시                                │
└─────────────────────────────────────────────┘
```

## 🔍 검색 조건

- ✅ 360도 회전 (2-in-1, x360, convertible)
- ✅ Thunderbolt 3/4 포함
- ✅ LTE/WWAN 모듈 탑재
- ✅ RAM 16GB 이상
- ✅ Intel i5 7세대 이상
- ✅ 가격: 30~60만원

## 📦 프로젝트 구조

```
notebook/
├── src/                      # React 소스
│   ├── App.jsx               # 메인 컴포넌트
│   ├── components/           # React 컴포넌트
│   │   ├── Header.jsx
│   │   ├── Stats.jsx
│   │   ├── Controls.jsx
│   │   └── ResultCard.jsx
│   ├── styles.css            # 스타일
│   └── main.jsx              # 엔트리
├── crawlers/                 # Python 크롤러
├── utils/                    # 유틸리티
├── data/                     # 크롤링 결과
│   └── results.json          # 자동 생성
├── .github/workflows/        # GitHub Actions
│   └── crawl-and-deploy.yml  # 자동화 워크플로우
├── index.html                # HTML 엔트리
├── package.json              # Node.js 설정
└── vite.config.js            # Vite 설정
```

## 🛠️ 로컬 개발

### 1. 저장소 클론

```bash
git clone https://github.com/liveq/notebook.git
cd notebook
```

### 2. 의존성 설치

```bash
# Node.js 의존성
npm install

# Python 의존성 (크롤링용)
pip install -r requirements.txt
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

### 4. 크롤링 테스트

```bash
python search_notebook.py
```

결과: `data/results.json` 생성

### 5. 빌드

```bash
npm run build
```

결과: `dist/` 디렉토리 생성

## 🤖 자동화 설정

### GitHub Actions가 자동으로 실행

**실행 시점:**
- 매일 자동 (UTC 00:00 / 한국시간 09:00)
- 코드 푸시 시
- 수동 실행 (Actions 탭에서 "Run workflow")

**실행 내용:**
1. Python 크롤링 실행
2. `data/results.json` 자동 업데이트
3. React 앱 빌드
4. GitHub Pages에 자동 배포

### 수동 실행 방법

1. GitHub 저장소 접속
2. **Actions** 탭 클릭
3. **"크롤링 & 배포"** 워크플로우 선택
4. **"Run workflow"** 버튼 클릭

## 📍 GitHub Pages 설정

### 첫 배포 시 설정 필요

1. **저장소 Settings** 이동
   ```
   https://github.com/liveq/notebook/settings
   ```

2. 좌측 메뉴에서 **"Pages"** 클릭

3. **Source** 설정:
   ```
   Branch: gh-pages
   Folder: / (root)
   ```

4. **Save** 클릭

5. 5분 후 접속 가능:
   ```
   https://liveq.github.io/notebook/
   ```

## 🎨 기능

### 메인 페이지
- 📊 통계 요약 (총 매물, 신규, 가격대)
- 🔍 검색 조건 표시
- 📱 반응형 카드 레이아웃

### 필터링
- 전체 매물 / 신규만 보기

### 정렬
- 최신순
- 가격 낮은순
- 가격 높은순

### 매물 카드
- 제목, 가격, 스펙 (CPU, RAM)
- 매칭 키워드
- 출처 (중고나라/번개장터/당근)
- 신규 매물 표시 (초록 테두리)
- 상세보기 링크

## 🌐 배포 URL

**프로덕션:**
```
https://liveq.github.io/notebook/
```

**GitHub Actions 로그:**
```
https://github.com/liveq/notebook/actions
```

## 💰 비용

**완전 무료!**
- GitHub Pages: 무료
- GitHub Actions: 월 2000분 무료 (크롤링 1회 약 2분)
- 저장 용량: 1GB 무료

## 🔧 문제 해결

### 크롤링 결과가 없는 경우

1. GitHub Actions 로그 확인
   ```
   저장소 → Actions 탭 → 최근 워크플로우 클릭
   ```

2. Python 의존성 확인
   ```bash
   pip install -r requirements.txt
   ```

### 배포가 안 되는 경우

1. GitHub Pages 설정 확인 (Settings → Pages)
2. `gh-pages` 브랜치 생성 확인
3. 워크플로우 권한 확인 (Settings → Actions → General)

### React 앱이 로드되지 않는 경우

1. 브라우저 콘솔 확인 (F12)
2. `data/results.json` 파일 존재 확인
3. CORS 에러 시 → GitHub Pages 재배포

## 📝 커스터마이징

### 검색 조건 변경

`config.py` 수정:
```python
SEARCH_CONDITIONS = {
    "min_price": 300000,
    "max_price": 600000,
    "min_ram": 16,
    # ...
}
```

### UI 스타일 변경

`src/styles.css` 수정

### 검색 키워드 추가

`config.py`의 `SEARCH_KEYWORDS` 수정

## 📊 모니터링

### GitHub Actions 상태

```
https://github.com/liveq/notebook/actions
```

실시간 로그, 성공/실패 확인

### 크롤링 결과

```
https://github.com/liveq/notebook/blob/main/data/results.json
```

최신 크롤링 결과 확인

## 🎯 장점

| 항목 | 기존 (Render) | 새로운 방식 (GitHub Pages) |
|------|---------------|---------------------------|
| 서버 | 필요 (Flask) | 불필요 (정적 사이트) |
| 비용 | 무료 (제한 있음) | 완전 무료 |
| 속도 | 슬립 모드 | 항상 빠름 |
| 배포 | 수동/자동 | 완전 자동 |
| 의존성 | Render 계정 | GitHub만 |

## 🚀 다음 단계

1. ✅ GitHub Actions로 크롤링 자동화
2. ✅ React로 UI 구현
3. ✅ GitHub Pages 배포
4. ⬜ 텔레그램 알림 추가
5. ⬜ PWA 지원
6. ⬜ 가격 변동 추적

## 📞 지원

- **이슈:** https://github.com/liveq/notebook/issues
- **Wiki:** https://github.com/liveq/notebook/wiki

---

**완전히 GitHub만 사용하는 중고 노트북 검색 서비스!** 🎉
