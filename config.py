"""
중고 노트북 LTE 매물 검색 프로그램 설정 파일
"""

# 검색 조건
SEARCH_CONDITIONS = {
    # 가격 범위 (원)
    "min_price": 300000,
    "max_price": 600000,

    # RAM 최소 용량 (GB)
    "min_ram": 16,

    # CPU 조건
    "cpu_generations": {
        "i5": [8, 9, 10, 11, 12, 13],  # i5 8세대 이상
        "i7": [8, 9, 10, 11, 12, 13],  # i7 8세대 이상
        "i9": [8, 9, 10, 11, 12, 13],  # i9 8세대 이상
    },

    # 필수 키워드 (하나 이상 포함되어야 함)
    "required_keywords": {
        "convertible": ["360", "2-in-1", "2in1", "x360", "convertible", "yoga", "flip"],
        "thunderbolt": ["thunderbolt", "tb3", "tb4", "썬더볼트"],
        "lte": ["lte", "wwan", "유심", "심슬롯", "4g", "5g"],
    },

    # 부정 키워드 (포함되면 제외)
    "negative_keywords": [
        "유심슬롯 없음",
        "유심없음",
        "lte없음",
        "wwan없음",
        "불량",
        "고장",
        "액정파손",
        "파손",
    ],
}

# 주요 검색 모델
TARGET_MODELS = [
    # HP EliteBook x360
    "elitebook x360 1030 g3",
    "elitebook x360 1030 g4",
    "elitebook x360 1040 g5",
    "elitebook x360 1040 g6",
    "elitebook x360 1040 g7",

    # ThinkPad X1 Yoga
    "x1 yoga 3rd",
    "x1 yoga 4th",
    "x1 yoga 5th",
    "x1 yoga gen 3",
    "x1 yoga gen 4",
    "x1 yoga gen 5",

    # Dell Latitude
    "latitude 7390 2-in-1",
    "latitude 7400 2-in-1",
]

# 검색 키워드 (다양한 키워드 조합)
SEARCH_KEYWORDS = [
    "노트북 lte",
    "노트북 wwan",
    "노트북 5g",
    "2in1 lte",
    "2-in-1 lte",
    "x360 lte",
    "x360 wwan",
    "convertible lte",
    "컨버터블 lte",
    "yoga lte",
    "yoga wwan",
    "wwan 노트북",
    "lte 탑재",
    "유심 노트북",
    "심슬롯 노트북",
    "elitebook x360",
    "elitebook 1030",
    "elitebook 1040",
    "x1 yoga",
    "thinkpad yoga",
    "latitude 2-in-1",
    "latitude 7390",
    "latitude 7400",
    "spectre x360",
    "zenbook flip",
    "360도 노트북",
    "터치 노트북 lte",
    "썬더볼트 lte",
]

# 크롤링 설정
CRAWLER_SETTINGS = {
    # 각 사이트 간 대기 시간 (초)
    "delay_between_sites": 3,

    # 각 요청 간 대기 시간 (초)
    "delay_between_requests": 2,

    # 타임아웃 (초)
    "timeout": 10,

    # User-Agent
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

    # 최대 검색 결과 수 (사이트당)
    "max_results_per_site": 50,
}

# 파일 경로
FILE_PATHS = {
    "results": "data/results.json",
    "previous_results": "data/previous_results.json",
    "html_output": "results.html",
    "log": "data/crawler.log",
}
