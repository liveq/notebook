# ⚠️ GitHub 저장소 설정 체크리스트

## 🔍 현재 상태 확인

코드는 모두 푸시되었지만, GitHub에서 **수동 설정이 필요**합니다!

---

## ✅ 필수 설정 (순서대로)

### 1️⃣ GitHub Actions 권한 설정

**위치:**
```
https://github.com/liveq/notebook/settings/actions
```

**경로:**
```
Settings (탭) → Actions (좌측 메뉴) → General
```

**설정 내용:**

#### ① Workflow permissions
```
✅ Read and write permissions  (선택)
✅ Allow GitHub Actions to create and approve pull requests (체크)
```

**왜 필요?**
- Actions가 `data/results.json` 파일을 커밋하려면 쓰기 권한 필요
- `gh-pages` 브랜치를 자동 생성하려면 필요

---

### 2️⃣ GitHub Pages 설정

**⚠️ 중요:** 처음에는 설정할 수 없습니다!

**순서:**
1. 먼저 GitHub Actions를 **한 번 실행**
2. `gh-pages` 브랜치가 자동 생성됨
3. 그 다음 Pages 설정 가능

**Actions 수동 실행:**
```
https://github.com/liveq/notebook/actions
→ "크롤링 & 배포" 워크플로우 선택
→ "Run workflow" 버튼 클릭
→ "Run workflow" 확인
```

**5-10분 후, Pages 설정:**

**위치:**
```
https://github.com/liveq/notebook/settings/pages
```

**설정:**
```
Source:
  Branch: gh-pages
  Folder: / (root)

[Save] 버튼 클릭
```

---

### 3️⃣ 브랜치 설정 (선택사항)

현재 `main` 브랜치가 없습니다.

**옵션 A: 현재 브랜치를 main으로**
```bash
git checkout -b main
git push -u origin main
```

**옵션 B: 현재 브랜치 그대로 사용**
- 그대로 사용해도 됩니다
- GitHub Actions는 현재 브랜치에서 작동합니다

---

## 📋 설정 확인 체크리스트

### ✅ 확인해야 할 것들

**1. Actions 권한**
- [ ] Settings → Actions → General
- [ ] "Read and write permissions" 선택됨
- [ ] "Allow GitHub Actions to create..." 체크됨

**2. Actions 실행**
- [ ] Actions 탭에서 워크플로우 보임
- [ ] 수동으로 실행 가능
- [ ] 실행 후 성공 (초록 체크)

**3. gh-pages 브랜치**
- [ ] Actions 실행 후 자동 생성됨
- [ ] 브랜치 목록에서 확인 가능

**4. Pages 설정**
- [ ] Settings → Pages
- [ ] Source: gh-pages 브랜치 선택
- [ ] Save 완료

**5. 배포 URL**
- [ ] https://liveq.github.io/notebook/ 접속 가능

---

## 🚨 예상되는 문제

### 문제 1: Actions 실행 권한 없음
**증상:**
```
Error: Resource not accessible by integration
```

**해결:**
```
Settings → Actions → General
→ "Read and write permissions" 선택
```

---

### 문제 2: gh-pages 브랜치 없음
**증상:**
```
Settings → Pages에서 브랜치 선택 불가
```

**해결:**
```
1. Actions 탭으로 이동
2. "Run workflow" 버튼으로 수동 실행
3. 성공 후 gh-pages 브랜치 자동 생성
```

---

### 문제 3: Python 의존성 오류
**증상:**
```
Actions 로그에 "ModuleNotFoundError"
```

**해결:**
```
requirements.txt 확인 (이미 있음)
→ 자동으로 설치됩니다
```

---

### 문제 4: Node.js 빌드 실패
**증상:**
```
npm ci 실패
```

**해결:**
```
로컬에서 확인:
npm install
npm run build

문제없으면 다시 Actions 실행
```

---

## 🎯 지금 바로 해야 할 것

### 단계별 가이드

**Step 1: Actions 권한 설정** ⭐ 가장 중요!
```
1. https://github.com/liveq/notebook/settings/actions 접속
2. "Workflow permissions" 섹션 찾기
3. "Read and write permissions" 선택
4. "Allow GitHub Actions to create and approve pull requests" 체크
5. [Save] 클릭
```

**Step 2: Actions 실행**
```
1. https://github.com/liveq/notebook/actions 접속
2. 좌측에서 "크롤링 & 배포" 클릭
3. 우측 상단 "Run workflow" 버튼
4. 브랜치 선택: claude/used-notebook-lte-crawler-011CUeJBMB3N9z5bCYmQa95g
5. 녹색 "Run workflow" 버튼 클릭
6. 5-10분 기다리기
```

**Step 3: 실행 결과 확인**
```
1. Actions 탭에서 실행 상태 확인
2. 초록 체크(✓) 나오면 성공
3. 빨간 X(✗) 나오면 로그 확인
```

**Step 4: gh-pages 브랜치 확인**
```
1. 저장소 메인 페이지
2. 브랜치 드롭다운 클릭
3. "gh-pages" 브랜치 있는지 확인
```

**Step 5: Pages 설정**
```
1. https://github.com/liveq/notebook/settings/pages
2. Source: gh-pages 선택
3. [Save] 클릭
4. 5분 기다리기
```

**Step 6: 접속 테스트**
```
https://liveq.github.io/notebook/
```

---

## 📸 스크린샷 위치 안내

### Actions 권한 설정 위치
```
GitHub 저장소 페이지
  ↓
상단 탭 "Settings" 클릭
  ↓
좌측 메뉴 "Actions" 클릭
  ↓
좌측 하위 메뉴 "General" 클릭
  ↓
아래로 스크롤
  ↓
"Workflow permissions" 섹션
```

### Pages 설정 위치
```
GitHub 저장소 페이지
  ↓
상단 탭 "Settings" 클릭
  ↓
좌측 메뉴 "Pages" 클릭 (Code and automation 섹션)
  ↓
"Source" 드롭다운
```

---

## 💡 팁

### Actions 자동 실행 시간
```
매일 한국시간 오전 9시
(또는 코드 푸시할 때마다)
```

### 수동 실행
```
언제든지 Actions 탭에서 "Run workflow"
```

### 로그 확인
```
Actions 탭 → 실행 중인 워크플로우 클릭 → 각 Job 클릭
```

---

## ❓ 문제 발생 시

**확인 순서:**
1. Actions 권한 설정 확인
2. Actions 로그 확인
3. 브랜치 목록 확인
4. Pages 설정 확인

**도움이 필요하면:**
- Actions 실행 로그 캡처
- 에러 메시지 복사
- 어느 단계에서 막혔는지 알려주세요

---

## ✅ 모든 설정 완료 후

**확인 사항:**
- ✅ Actions가 성공적으로 실행됨
- ✅ gh-pages 브랜치 생성됨
- ✅ Pages 설정 완료
- ✅ 웹사이트 접속 가능

**이제 완전 자동화!**
- 코드 푸시하면 자동 배포
- 매일 자동 크롤링
- GitHub만으로 완벽한 서비스 운영

---

지금 바로 **Step 1 (Actions 권한 설정)**부터 시작해보세요!
문제가 생기면 어느 단계에서 막혔는지 알려주세요! 🚀
