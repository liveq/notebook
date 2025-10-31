#!/usr/bin/env python3
"""
중고 노트북 LTE 매물 검색 웹 서비스
Flask 기반 웹 애플리케이션
"""
from flask import Flask, render_template, jsonify, request
import threading
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

from config import SEARCH_KEYWORDS, FILE_PATHS
from crawlers.joonggonara import JoonggonaraCrawler
from crawlers.bunjang import BunjangCrawler
from crawlers.daangn import DaangnCrawler
from utils.filters import NotebookFilter
from utils.storage import ResultStorage

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 검색 상태 저장
search_status = {
    'is_running': False,
    'progress': 0,
    'current_site': '',
    'total_found': 0,
    'filtered_count': 0,
    'message': '대기 중',
    'results': [],
    'stats': {},
    'error': None,
    'start_time': None,
    'end_time': None
}

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_search():
    """백그라운드에서 검색 실행"""
    global search_status

    try:
        search_status['is_running'] = True
        search_status['progress'] = 0
        search_status['message'] = '검색 준비 중...'
        search_status['error'] = None
        search_status['start_time'] = datetime.now().isoformat()
        search_status['end_time'] = None

        # 크롤러 초기화
        crawlers = [
            JoonggonaraCrawler(),
            BunjangCrawler(),
            DaangnCrawler()
        ]

        filter_obj = NotebookFilter()
        storage = ResultStorage()

        all_items = []
        total_crawlers = len(crawlers)

        # 1. 크롤링
        for idx, crawler in enumerate(crawlers):
            try:
                search_status['current_site'] = crawler.source_name
                search_status['message'] = f'{crawler.source_name} 검색 중...'
                search_status['progress'] = int((idx / total_crawlers) * 50)

                logger.info(f"[{crawler.source_name}] 검색 시작")
                items = crawler.search(SEARCH_KEYWORDS)
                all_items.extend(items)

                search_status['total_found'] = len(all_items)
                logger.info(f"[{crawler.source_name}] {len(items)}개 발견")

                time.sleep(2)  # 사이트 간 대기

            except Exception as e:
                logger.error(f"[{crawler.source_name}] 크롤링 실패: {e}")
                continue

        search_status['progress'] = 50
        search_status['message'] = '매물 필터링 중...'

        # 2. 필터링
        filtered_items = filter_obj.filter_items(all_items)
        search_status['filtered_count'] = len(filtered_items)
        search_status['progress'] = 70

        # 3. 중복 제거
        search_status['message'] = '중복 제거 중...'
        unique_items = storage.remove_duplicates(filtered_items)
        search_status['progress'] = 80

        # 4. 신규 매물 확인
        search_status['message'] = '신규 매물 확인 중...'
        new_items = storage.find_new_items(unique_items)
        search_status['progress'] = 90

        # 5. 통계 생성
        stats = storage.get_statistics(unique_items)

        # 6. 결과 저장
        storage.save_results(unique_items)
        search_status['progress'] = 100

        # 결과 저장
        search_status['results'] = unique_items
        search_status['stats'] = stats
        search_status['message'] = '검색 완료!'
        search_status['end_time'] = datetime.now().isoformat()

        logger.info(f"검색 완료: 총 {len(unique_items)}개, 신규 {len(new_items)}개")

    except Exception as e:
        logger.error(f"검색 중 오류: {e}", exc_info=True)
        search_status['error'] = str(e)
        search_status['message'] = f'오류 발생: {e}'
        search_status['progress'] = 0

    finally:
        search_status['is_running'] = False


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/start-search', methods=['POST'])
def start_search():
    """검색 시작"""
    global search_status

    if search_status['is_running']:
        return jsonify({
            'success': False,
            'message': '이미 검색이 진행 중입니다.'
        }), 400

    # 검색 상태 초기화
    search_status = {
        'is_running': True,
        'progress': 0,
        'current_site': '',
        'total_found': 0,
        'filtered_count': 0,
        'message': '검색 시작',
        'results': [],
        'stats': {},
        'error': None,
        'start_time': None,
        'end_time': None
    }

    # 백그라운드 스레드로 검색 시작
    thread = threading.Thread(target=run_search)
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': '검색이 시작되었습니다.'
    })


@app.route('/search-status')
def get_search_status():
    """검색 상태 조회"""
    return jsonify(search_status)


@app.route('/results')
def results():
    """결과 페이지"""
    return render_template('results.html')


@app.route('/api/results')
def api_results():
    """결과 데이터 API"""
    storage = ResultStorage()
    results = storage.load_results()
    stats = storage.get_statistics(results)

    return jsonify({
        'results': results,
        'stats': stats
    })


@app.route('/health')
def health():
    """헬스 체크"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       중고 노트북 LTE 매물 검색 웹 서비스               ║
    ║                                                          ║
    ║  접속 주소:                                              ║
    ║  - 로컬: http://localhost:5000                          ║
    ║  - 네트워크: http://0.0.0.0:5000                        ║
    ║                                                          ║
    ║  스마트폰으로 접속하려면:                                ║
    ║  같은 WiFi에 연결 후 컴퓨터의 IP:5000 접속              ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # 0.0.0.0으로 바인딩하여 외부 접속 허용
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
