# 중고 노트북 LTE 매물 자동 검색 웹 서비스

![Deploy](https://github.com/liveq/notebook/actions/workflows/deploy.yml/badge.svg)
![CI](https://github.com/liveq/notebook/actions/workflows/ci.yml/badge.svg)

매일 중고나라, 번개장터, 당근마켓에서 LTE가 탑재된 2-in-1 노트북을 자동으로 검색하고, 조건에 맞는 매물만 필터링하여 **웹 브라우저(모바일/데스크탑)**에서 확인할 수 있는 웹 서비스입니다.

## 🚀 빠른 시작

**배포된 서비스 사용:**
```
https://your-app-name.onrender.com
```

**GitHub에 푸시하면 자동 배포됩니다!**

## 주요 기능

✅ **웹 기반 서비스**
- 버튼 클릭 한 번으로 검색 시작
- 실시간 진행률 표시
- 모바일 & 데스크탑 모두 지원

✅ **3개 플랫폼 자동 검색**
- 중고나라 (네이버 카페)
- 번개장터
- 당근마켓

✅ **스마트한 필터링**
- 360도 회전 가능 (2-in-1, convertible)
- Thunderbolt 3/4 포함
- LTE/WWAN 모듈 탑재
- RAM 16GB 이상
- Intel i5 7세대 이상
- 가격: 30~60만원

✅ **반응형 웹 인터페이스**
- 모바일 최적화 (스마트폰에서 편리하게)
- 데스크탑 최적화
- 실시간 검색 진행 상황 확인
- 가격순/최신순 정렬 기능
- 신규 매물 표시

✅ **중복 제거 & 신규 알림**
- URL 기준 중복 매물 자동 제거
- 이전 검색과 비교하여 신규 매물만 표시

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/liveq/notebook.git
cd notebook
git checkout claude/save-missing-code-011CUeSJXKciYKGzKiWPBLd6
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

또는 자동 실행 스크립트 사용:
```bash
chmod +x run.sh
./run.sh
```

## 사용 방법

### 웹 서비스 실행

#### 방법 1: 자동 스크립트 사용 (권장)
```bash
./run.sh
```

#### 방법 2: 직접 실행
```bash
python app.py
```

### 접속 방법

서버가 시작되면 다음 주소로 접속:

#### 🖥️ 데스크탑에서
```
http://localhost:5000
```

#### 📱 스마트폰에서
1. 컴퓨터와 **같은 WiFi**에 연결
2. 터미널에 표시된 네트워크 주소로 접속
   ```
   http://[컴퓨터IP]:5000
   예: http://192.168.0.100:5000
   ```

### 사용 순서
1. 웹 브라우저에서 접속
2. **"검색 시작"** 버튼 클릭
3. 진행률 확인 (1-2분 소요)
4. **"결과 보기"** 버튼 클릭
5. 매물 확인 및 필터링/정렬

## 프로젝트 구조

```
notebook/
├── app.py                   # Flask 웹 애플리케이션
├── search_notebook.py       # CLI 버전 (선택사항)
├── config.py                # 설정 파일
├── run.sh                   # 실행 스크립트
├── templates/               # HTML 템플릿
│   ├── index.html           # 메인 페이지
│   └── results.html         # 결과 페이지
├── static/                  # 정적 파일
│   └── css/
│       └── style.css        # 스타일시트
├── crawlers/                # 크롤러 모듈
│   ├── base_crawler.py      # 기본 크롤러 클래스
│   ├── joonggonara.py       # 중고나라 크롤러
│   ├── bunjang.py           # 번개장터 크롤러
│   └── daangn.py            # 당근마켓 크롤러
├── utils/                   # 유틸리티 모듈
│   ├── filters.py           # 필터링 로직
│   ├── storage.py           # 결과 저장/로드
│   └── html_generator.py    # HTML 생성
├── data/                    # 데이터 디렉토리
│   ├── results.json         # 검색 결과
│   ├── previous_results.json # 이전 검색 결과
│   └── crawler.log          # 로그 파일
└── requirements.txt         # 필수 패키지
```

## 웹 서비스 화면

### 메인 페이지
- 검색 조건 확인
- 검색 시작 버튼
- 실시간 진행률 표시
- 현재 검색 중인 사이트 표시
- 발견된 매물 수 실시간 업데이트

### 결과 페이지
- 통계 요약 (총 매물, 신규 매물, 가격대)
- 필터 버튼 (전체/신규)
- 정렬 버튼 (최신순/가격 낮은순/높은순)
- 매물 카드 (제목, 가격, 스펙, 위치, 링크)
- 신규 매물 강조 표시

## API 엔드포인트

```
GET  /                  # 메인 페이지
POST /start-search      # 검색 시작
GET  /search-status     # 검색 상태 조회
GET  /results           # 결과 페이지
GET  /api/results       # 결과 데이터 (JSON)
GET  /health            # 헬스 체크
```

## 설정 커스터마이징

`config.py` 파일을 수정하여 검색 조건을 변경할 수 있습니다:

```python
SEARCH_CONDITIONS = {
    "min_price": 300000,      # 최소 가격 (원)
    "max_price": 600000,      # 최대 가격 (원)
    "min_ram": 16,            # 최소 RAM (GB)
    "cpu_generations": {
        "i5": [7, 8, 9, 10, 11, 12, 13],
        "i7": [7, 8, 9, 10, 11, 12, 13],
    },
}

SEARCH_KEYWORDS = [
    "노트북 lte",
    "2in1 lte",
    "x360 lte",
    # 추가 키워드...
]
```

## 검색 대상 모델

- HP EliteBook x360 1030 G3/G4
- HP EliteBook x360 1040 G5/G6/G7
- ThinkPad X1 Yoga 3rd/4th/5th Gen
- Dell Latitude 7390/7400 2-in-1

## 주의사항

⚠️ **웹 크롤링 정책**
- 각 사이트의 `robots.txt`를 준수합니다
- 과도한 요청을 방지하기 위해 요청 간 대기 시간을 둡니다
- 사이트 정책에 따라 로그인이 필요할 수 있습니다

⚠️ **실제 사용 시 고려사항**
- 중고나라는 네이버 로그인이 필요할 수 있습니다
- 번개장터와 당근마켓은 동적 렌더링을 사용할 수 있어 Selenium이 필요할 수 있습니다
- 사이트 구조 변경 시 크롤러 코드 수정이 필요할 수 있습니다

⚠️ **법적 고지**
- 이 프로그램은 개인적인 용도로만 사용하세요
- 상업적 목적이나 대량 크롤링은 금지됩니다
- 각 플랫폼의 이용약관을 준수하세요

⚠️ **네트워크 보안**
- 웹 서비스는 0.0.0.0:5000으로 바인딩되어 네트워크 내 모든 기기에서 접근 가능합니다
- 공용 네트워크에서는 사용에 주의하세요
- 프로덕션 환경에서는 HTTPS 및 인증을 추가하세요

## 스크린샷

### 모바일 화면
- 검색 시작 화면 (버튼 큼, 터치 최적화)
- 진행률 표시 (실시간)
- 결과 카드 (세로 스크롤)

### 데스크탑 화면
- 넓은 화면 활용 (그리드 레이아웃)
- 한눈에 여러 매물 확인
- 상세한 필터링/정렬 옵션

## 문제 해결

### 포트 5000이 이미 사용 중인 경우
`app.py`에서 포트 변경:
```python
app.run(host='0.0.0.0', port=8000, debug=True)
```

### Flask가 설치되지 않은 경우
```bash
pip install Flask
```

### 스마트폰에서 접속이 안 되는 경우
1. 같은 WiFi에 연결되어 있는지 확인
2. 방화벽 설정 확인
3. 컴퓨터의 IP 주소 확인:
   ```bash
   # Linux/Mac
   ifconfig
   # Windows
   ipconfig
   ```

### 크롤링이 작동하지 않는 경우
1. `data/crawler.log` 파일 확인
2. 인터넷 연결 확인
3. 사이트 접근 가능 여부 확인

## CLI 버전 사용 (선택사항)

웹 서비스 대신 명령줄에서 실행:
```bash
python search_notebook.py
```
결과는 `results.html` 파일로 생성됩니다.

## 배포 (선택사항)

### Heroku
```bash
# Procfile 생성
echo "web: python app.py" > Procfile

# 배포
heroku create
git push heroku main
```

### Docker
```bash
# Dockerfile 생성 후
docker build -t notebook-search .
docker run -p 5000:5000 notebook-search
```

## 향후 개선 계획

- [ ] Selenium을 이용한 동적 페이지 크롤링
- [ ] 텔레그램/이메일 알림 기능
- [ ] 사용자 계정 및 즐겨찾기 기능
- [ ] 가격 변동 추적 그래프
- [ ] 더 많은 플랫폼 지원
- [ ] 자동 스케줄링 (매일 자동 검색)
- [ ] PWA (Progressive Web App) 지원

## 라이선스

MIT License

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

## 문의

- GitHub: https://github.com/liveq/notebook
- 이슈 트래커: https://github.com/liveq/notebook/issues

---

**면책 조항**: 이 프로그램은 교육 목적으로 제작되었습니다. 사용자는 각 플랫폼의 이용약관을 준수할 책임이 있습니다.
