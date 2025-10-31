# GitHub 자동 배포 설정 가이드

GitHub에 푸시하면 자동으로 배포되도록 설정하는 방법입니다.

## ✅ 이미 완료된 것

1. **GitHub Actions 워크플로우 파일** ✅
   - `.github/workflows/deploy.yml` - 자동 배포
   - `.github/workflows/ci.yml` - 코드 검증

2. **배포 설정 파일** ✅
   - `render.yaml` - Render 배포 설정
   - `Procfile` - 웹 서버 설정

---

## 🚀 GitHub Actions 작동 방식

### 자동으로 실행되는 경우

#### 1. 코드 검증 (CI)
**언제:** 모든 브랜치에 push 또는 PR 생성 시
**동작:**
- Python 문법 검증
- 파일 구조 확인
- Flask 앱 로드 테스트

#### 2. 자동 배포
**언제:** 메인 브랜치에 push 시
**동작:**
- 코드 검증 실행
- Render에 배포 알림
- 배포 상태 확인

---

## 🔧 GitHub Secrets 설정 (선택사항)

Render Deploy Hook을 사용하려면 GitHub Secrets 설정이 필요합니다.

### 1단계: Render Deploy Hook URL 가져오기

1. **Render 대시보드** 접속
   - https://dashboard.render.com

2. **Web Service 선택**
   - 배포한 앱 클릭

3. **Settings 탭** 이동

4. **"Deploy Hook"** 섹션 찾기
   - "Create Deploy Hook" 클릭
   - Hook 이름 입력: `GitHub Actions`
   - URL이 생성됨 (예: `https://api.render.com/deploy/srv-xxx?key=yyy`)
   - **이 URL을 복사**

### 2단계: GitHub Secrets에 추가

1. **GitHub 저장소** 접속
   ```
   https://github.com/liveq/notebook
   ```

2. **Settings 탭** 클릭
   ```
   위치: 저장소 상단 메뉴의 "Settings"
   ```

3. **좌측 메뉴에서 "Secrets and variables" → "Actions"** 클릭
   ```
   위치: Settings → 좌측 메뉴 → Security → Secrets and variables → Actions
   ```

4. **"New repository secret"** 버튼 클릭

5. **Secret 추가**
   ```
   Name: RENDER_DEPLOY_HOOK_URL
   Value: [1단계에서 복사한 Deploy Hook URL]
   ```

6. **"Add secret"** 클릭

### ✅ 설정 완료!

이제 GitHub에 푸시하면 Render가 자동으로 재배포됩니다!

---

## 📍 GitHub 설정 위치 정리

### 1. Actions 워크플로우 확인
```
GitHub 저장소 → Actions 탭
```
여기서 워크플로우 실행 상태를 볼 수 있습니다.

### 2. Secrets 설정 위치
```
GitHub 저장소 → Settings → Secrets and variables → Actions
```

### 3. Actions 활성화 확인
```
GitHub 저장소 → Settings → Actions → General
```
"Allow all actions and reusable workflows" 선택 확인

---

## 🔄 자동 배포 테스트

### 1. 코드 수정 후 푸시
```bash
git add .
git commit -m "테스트: 자동 배포"
git push
```

### 2. GitHub Actions 확인
1. GitHub 저장소의 **"Actions"** 탭 클릭
2. 실행 중인 워크플로우 확인
3. 로그 실시간 확인

### 3. Render 배포 확인
1. Render 대시보드 접속
2. 배포 로그 확인
3. 배포 완료 후 앱 접속

---

## 📊 워크플로우 상태 배지 (선택사항)

README.md에 배지 추가:

```markdown
![Deploy](https://github.com/liveq/notebook/actions/workflows/deploy.yml/badge.svg)
![CI](https://github.com/liveq/notebook/actions/workflows/ci.yml/badge.svg)
```

---

## ⚙️ 고급 설정 (선택사항)

### 특정 브랜치만 자동 배포

`.github/workflows/deploy.yml` 수정:
```yaml
on:
  push:
    branches:
      - main  # main 브랜치만
      # - claude/save-missing-code-011CUeSJXKciYKGzKiWPBLd6  # 주석 처리
```

### 배포 전 승인 필요

```yaml
deploy:
  needs: test
  environment: production  # 추가
  runs-on: ubuntu-latest
```

그 다음 GitHub Settings → Environments에서 승인자 설정

---

## 🐛 문제 해결

### Actions가 실행되지 않는 경우

1. **Actions 활성화 확인**
   - Settings → Actions → General
   - "Allow all actions" 선택

2. **워크플로우 파일 위치 확인**
   ```
   .github/workflows/deploy.yml
   .github/workflows/ci.yml
   ```

3. **YAML 문법 확인**
   - GitHub Actions 탭에서 오류 메시지 확인

### 배포가 트리거되지 않는 경우

1. **Render Deploy Hook 확인**
   - Render Settings → Deploy Hook
   - URL이 GitHub Secrets에 정확히 입력되었는지 확인

2. **Secret 이름 확인**
   - 정확히 `RENDER_DEPLOY_HOOK_URL`인지 확인

3. **워크플로우 로그 확인**
   - GitHub Actions 탭에서 상세 로그 확인

---

## 📞 도움말

### GitHub Actions 문서
- https://docs.github.com/actions

### Render Deploy Hooks 문서
- https://render.com/docs/deploy-hooks

### GitHub Secrets 설정 가이드
- https://docs.github.com/actions/security-guides/encrypted-secrets

---

## 🎉 완료!

이제 다음이 자동으로 실행됩니다:

1. ✅ **코드 푸시** → GitHub Actions 실행
2. ✅ **코드 검증** → 문법 체크, 구조 확인
3. ✅ **자동 배포** → Render에 배포
4. ✅ **배포 완료** → 앱 자동 업데이트

**더 이상 수동으로 배포할 필요가 없습니다!** 🚀
