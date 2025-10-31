#!/usr/bin/env python3
"""
중고 노트북 LTE 매물 자동 검색 프로그램 (구글 검색 기반)

구글 검색 결과에서 중고나라/번개장터/당근마켓 링크를 수집합니다.
"""
import sys
import logging
from typing import List, Dict, Any

# 로컬 모듈 임포트
from config import SEARCH_KEYWORDS, FILE_PATHS
from crawlers.google_search import GoogleSearchCrawler
from utils.storage import ResultStorage


class NotebookSearcher:
    """중고 노트북 검색 메인 클래스"""

    def __init__(self):
        """초기화"""
        self.setup_logging()
        self.logger = logging.getLogger("NotebookSearcher")

        # 크롤러 초기화
        self.crawler = GoogleSearchCrawler()

        # 스토리지 초기화
        self.storage = ResultStorage()

    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(FILE_PATHS['log'], encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def run(self) -> bool:
        """
        검색 실행

        Returns:
            성공 여부
        """
        try:
            self.print_header()

            self.logger.info("=" * 60)
            self.logger.info("구글 검색 기반 중고 매물 수집 시작")
            self.logger.info("=" * 60)

            # 1. 구글 검색으로 모든 플랫폼 크롤링
            platform_results = self.crawler.search_all_platforms(SEARCH_KEYWORDS)

            # 2. 모든 결과 합치기
            all_items = []
            for platform, items in platform_results.items():
                all_items.extend(items)
                self.logger.info(f"[{platform}] {len(items)}개 수집")

            self.logger.info(f"총 {len(all_items)}개 매물 수집 완료")

            if not all_items:
                self.logger.warning("수집된 매물이 없습니다.")
                # 빈 결과 저장
                self.storage.save_results([])
                return False

            # 3. 결과 저장
            self.storage.save_results(all_items)
            self.logger.info(f"결과 저장 완료: {FILE_PATHS['results']}")

            return True

        except Exception as e:
            self.logger.error(f"검색 실행 중 오류 발생: {e}", exc_info=True)
            return False

    def print_header(self):
        """헤더 출력"""
        header = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       중고 노트북 LTE 매물 자동 검색 (구글 검색)        ║
    ║                                                          ║
    ║  검색 방식:                                              ║
    ║   - 구글 검색 결과에서 링크 수집                        ║
    ║   - 중고나라, 번개장터, 당근마켓                        ║
    ║   - 제목 + URL만 수집 (상세정보 없음)                   ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
        print(header)


def main():
    """메인 함수"""
    searcher = NotebookSearcher()

    success = searcher.run()

    if success:
        print("\n✅ 검색이 완료되었습니다!")
        print(f"📄 결과 파일: {FILE_PATHS['results']}")
    else:
        print("\n⚠️ 검색이 완료되었지만 결과가 없거나 문제가 발생했습니다.")
        print(f"📋 로그 파일을 확인하세요: {FILE_PATHS['log']}")


if __name__ == "__main__":
    main()
