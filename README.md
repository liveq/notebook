# 중고 노트북 LTE 매물 자동 검색 프로그램

매일 중고나라, 번개장터, 당근마켓에서 LTE가 탑재된 2-in-1 노트북을 자동으로 검색하고, 조건에 맞는 매물만 필터링하여 스마트폰에서 확인할 수 있는 프로그램입니다.

## 주요 기능

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

✅ **모바일 최적화**
- 반응형 HTML 생성
- 스마트폰에서 편리하게 확인
- 가격순/최신순 정렬 기능
- 신규 매물 표시

✅ **중복 제거 & 신규 알림**
- URL 기준 중복 매물 자동 제거
- 이전 검색과 비교하여 신규 매물만 표시

## 설치 방법

### 1. 저장소 클론 (또는 파일 다운로드)
```bash
git clone <repository-url>
cd notebook
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

## 사용 방법

### 기본 실행
```bash
python search_notebook.py
```

### 실행 결과
- `results.html`: 검색 결과를 보여주는 HTML 파일
- `data/results.json`: 검색 결과 JSON 데이터
- `data/crawler.log`: 실행 로그

### 스마트폰에서 확인하기
1. `results.html` 파일을 스마트폰으로 전송 (이메일, 클라우드 등)
2. 스마트폰 브라우저로 파일 열기
3. 매물 확인 및 링크 클릭하여 상세 페이지로 이동

## 프로젝트 구조

```
notebook/
├── search_notebook.py      # 메인 실행 파일
├── config.py                # 설정 파일
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
├── results.html             # 출력 HTML
├── requirements.txt         # 필수 패키지
└── README.md                # 프로젝트 설명
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

## 자동화 설정 (선택사항)

### Linux/Mac (cron)
매일 오전 9시에 자동 실행:
```bash
crontab -e

# 다음 줄 추가
0 9 * * * cd /path/to/notebook && python search_notebook.py
```

### Windows (작업 스케줄러)
1. 작업 스케줄러 열기
2. "기본 작업 만들기" 선택
3. 트리거: 매일
4. 작업: 프로그램 시작 - `python search_notebook.py`

## 문제 해결

### 크롤링이 작동하지 않는 경우
1. `data/crawler.log` 파일 확인
2. 인터넷 연결 확인
3. 사이트 접근 가능 여부 확인 (방화벽, VPN 등)

### 결과가 없는 경우
1. 검색 조건이 너무 엄격한지 확인
2. `config.py`에서 조건 완화 (가격 범위 확대, CPU 세대 낮추기 등)

### 의존성 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## 향후 개선 계획

- [ ] Selenium을 이용한 동적 페이지 크롤링
- [ ] 텔레그램/이메일 알림 기능
- [ ] 더 많은 플랫폼 지원 (알리익스프레스 중고, 옥션 등)
- [ ] 가격 변동 추적 기능
- [ ] 머신러닝 기반 매물 품질 평가

## 라이선스

MIT License

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

## 문의

- 이슈 트래커: <repository-url>/issues
- 이메일: your-email@example.com

---

**면책 조항**: 이 프로그램은 교육 목적으로 제작되었습니다. 사용자는 각 플랫폼의 이용약관을 준수할 책임이 있습니다.
