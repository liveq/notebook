# 중고 노트북 매물 체크 시스템

중고 노트북 매물이 특정 조건을 만족하는지 확인하는 웹 애플리케이션입니다.

## 배포된 사이트

https://liveq.github.io/notebook/

## 주요 기능

- **매물 정보 입력**: 제조사, 모델명, 스펙 등 11개 필드 입력
- **실시간 조건 체크**: 6가지 필수 조건 실시간 검증
  - CPU: Intel i5 8세대 이상
  - RAM: 16GB 이상
  - LTE/WWAN/5G 지원
  - 360도 회전 (2-in-1)
  - 터치 패널
  - 썬더볼트 3 이상
- **매물 리스트 관리**: 추가, 삭제, 조건 충족 상태 표시
- **JSON 저장/불러오기**: 데이터 백업 및 복원

## 기술 스택

- 순수 HTML/CSS/JavaScript (프레임워크 없음)
- GitHub Pages 자동 배포

## 파일 구조

```
.
├── index.html      # 메인 페이지
├── styles.css      # 스타일시트 (화이트골드 디자인)
├── script.js       # 로직 및 기능
└── .github/
    └── workflows/
        └── deploy.yml  # GitHub Actions 배포 설정
```

## 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/liveq/notebook.git
cd notebook

# 로컬 서버 실행 (Python)
python -m http.server 8000

# 또는 (Node.js)
npx serve

# 브라우저에서 접속
# http://localhost:8000
```

## 사용 방법

1. 매물 정보를 입력합니다
2. 실시간으로 6가지 조건 충족 여부를 확인합니다
3. '추가' 버튼을 클릭하여 리스트에 추가합니다
4. 'JSON 저장' 버튼으로 데이터를 백업할 수 있습니다
5. 'JSON 불러오기'로 이전에 저장한 데이터를 불러올 수 있습니다

## 라이선스

MIT License
