# 중고 노트북 LTE 매물 자동 검색

중고나라, 번개장터, 당근마켓에서 조건에 맞는 노트북 LTE 매물을 자동으로 검색하고 표시합니다.

## 배포된 사이트

https://liveq.github.io/notebook/

## 검색 조건

다음 6가지 조건을 모두 만족하는 매물을 검색합니다:

- **CPU**: Intel i5 8세대 이상
- **RAM**: 16GB 이상
- **LTE**: LTE/WWAN/5G 지원
- **360도 회전**: 2-in-1 컨버터블
- **터치 패널**: 터치스크린
- **썬더볼트**: Thunderbolt 3 이상

## 주요 기능

- 자동 크롤링 (GitHub Actions)
- 표 형태로 결과 표시
- 가격순 정렬 (오름차순/내림차순)
- 신규 매물 필터
- 화이트골드 디자인
- 반응형 (모바일/데스크탑)

## 사용 방법

1. https://liveq.github.io/notebook/ 접속
2. "최신 결과 보기" 버튼 클릭
3. 매물 확인 및 필터/정렬
4. "보기" 버튼으로 원본 사이트 이동

## 자동 크롤링

GitHub Actions에서 자동으로 크롤링을 실행합니다:

- **수동 실행**: GitHub Actions 탭에서 "Run workflow" 클릭
- **자동 실행**: 코드 푸시 시 자동 실행

## 프로젝트 구조

```
.
├── index.html          # 메인 페이지
├── styles.css          # 스타일시트
├── script.js           # 결과 표시 로직
├── search_notebook.py  # Python 크롤러
├── config.py           # 검색 조건 설정
├── crawlers/           # 크롤러 모듈
├── utils/              # 유틸리티
└── data/
    └── results.json    # 검색 결과
```

## 기술 스택

- **프론트엔드**: 순수 HTML/CSS/JavaScript
- **크롤러**: Python 3.11 + Requests
- **배포**: GitHub Pages + GitHub Actions

## 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/liveq/notebook.git
cd notebook

# Python 의존성 설치
pip install -r requirements.txt

# 크롤링 실행
python search_notebook.py

# 로컬 서버 실행
python -m http.server 8000
```

## 라이선스

MIT License
