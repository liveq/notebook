#!/usr/bin/env python3
"""
중고 노트북 LTE 매물 자동 검색 프로그램

사용법:
    python search_notebook.py

출력:
    - results.html: 검색 결과를 모바일 최적화된 HTML로 출력
    - data/results.json: 검색 결과를 JSON으로 저장
"""
import sys
import time
import logging
from typing import List, Dict, Any

# 로컬 모듈 임포트
from config import SEARCH_KEYWORDS, CRAWLER_SETTINGS, FILE_PATHS
from crawlers.joonggonara import JoonggonaraCrawler
from crawlers.bunjang import BunjangCrawler
from crawlers.daangn import DaangnCrawler
from utils.filters import NotebookFilter
from utils.storage import ResultStorage
from utils.html_generator import HTMLGenerator


class NotebookSearcher:
    """중고 노트북 검색 메인 클래스"""

    def __init__(self):
        """초기화"""
        self.setup_logging()
        self.logger = logging.getLogger("NotebookSearcher")

        # 크롤러 초기화
        self.crawlers = [
            JoonggonaraCrawler(),
            BunjangCrawler(),
            DaangnCrawler()
        ]

        # 유틸리티 초기화
        self.filter = NotebookFilter()
        self.storage = ResultStorage()
        self.html_gen = HTMLGenerator()

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
            self.logger.info("=" * 60)
            self.logger.info("중고 노트북 LTE 매물 검색 시작")
            self.logger.info("=" * 60)

            # 1. 크롤링
            all_items = self.crawl_all_sites()
            self.logger.info(f"총 {len(all_items)}개 매물 수집 완료")

            if not all_items:
                self.logger.warning("수집된 매물이 없습니다.")
                return False

            # 2. 필터링
            filtered_items = self.filter_items(all_items)
            self.logger.info(f"필터링 후 {len(filtered_items)}개 매물")

            if not filtered_items:
                self.logger.warning("조건에 맞는 매물이 없습니다.")
                # 빈 결과라도 HTML 생성
                self.generate_output([], {})
                return True

            # 3. 중복 제거
            unique_items = self.storage.remove_duplicates(filtered_items)
            self.logger.info(f"중복 제거 후 {len(unique_items)}개 매물")

            # 4. 신규 매물 확인
            new_items = self.storage.find_new_items(unique_items)
            self.logger.info(f"신규 매물 {len(new_items)}개 발견")

            # 5. 통계 생성
            stats = self.storage.get_statistics(unique_items)

            # 6. 결과 저장
            self.storage.save_results(unique_items)
            self.logger.info("결과 저장 완료")

            # 7. HTML 생성
            self.generate_output(unique_items, stats)

            self.logger.info("=" * 60)
            self.logger.info("검색 완료!")
            self.logger.info(f"총 매물: {stats['total_count']}개")
            self.logger.info(f"신규 매물: {stats['new_count']}개")
            self.logger.info(f"HTML 파일: {FILE_PATHS['html_output']}")
            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"검색 중 오류 발생: {e}", exc_info=True)
            return False

    def crawl_all_sites(self) -> List[Dict[str, Any]]:
        """
        모든 사이트에서 크롤링

        Returns:
            수집된 매물 리스트
        """
        all_items = []

        for crawler in self.crawlers:
            try:
                self.logger.info(f"\n[{crawler.source_name}] 검색 시작...")

                # 크롤링 실행
                items = crawler.search(SEARCH_KEYWORDS)

                self.logger.info(f"[{crawler.source_name}] {len(items)}개 매물 수집")
                all_items.extend(items)

                # 사이트 간 대기
                time.sleep(CRAWLER_SETTINGS['delay_between_sites'])

            except Exception as e:
                self.logger.error(f"[{crawler.source_name}] 크롤링 실패: {e}")
                continue

        return all_items

    def filter_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        매물 필터링

        Args:
            items: 원본 매물 리스트

        Returns:
            필터링된 매물 리스트
        """
        self.logger.info("\n매물 필터링 중...")

        filtered = self.filter.filter_items(items)

        # 필터링 통계
        total = len(items)
        passed = len(filtered)
        failed = total - passed

        self.logger.info(f"필터링 결과: {passed}/{total} 통과, {failed} 제외")

        return filtered

    def generate_output(self, results: List[Dict[str, Any]], stats: Dict[str, Any]):
        """
        결과 출력 파일 생성

        Args:
            results: 검색 결과
            stats: 통계 정보
        """
        try:
            # HTML 생성
            html_path = FILE_PATHS['html_output']
            success = self.html_gen.save_html(results, stats, html_path)

            if success:
                self.logger.info(f"HTML 파일 생성 완료: {html_path}")
            else:
                self.logger.error("HTML 파일 생성 실패")

        except Exception as e:
            self.logger.error(f"출력 파일 생성 중 오류: {e}")


def main():
    """메인 함수"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       중고 노트북 LTE 매물 자동 검색 프로그램           ║
    ║                                                          ║
    ║  검색 조건:                                              ║
    ║   - 360도 회전 가능 (2-in-1)                            ║
    ║   - Thunderbolt 3/4 포함                                ║
    ║   - LTE/WWAN 모듈 탑재                                  ║
    ║   - RAM 16GB 이상                                       ║
    ║   - Intel i5 7세대 이상                                 ║
    ║   - 가격: 30~60만원                                     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    try:
        searcher = NotebookSearcher()
        success = searcher.run()

        if success:
            print("\n✅ 검색 완료! results.html 파일을 확인하세요.")
            print(f"📱 스마트폰에서 {FILE_PATHS['html_output']} 파일을 열어보세요.")
            sys.exit(0)
        else:
            print("\n⚠️ 검색이 완료되었지만 결과가 없거나 문제가 발생했습니다.")
            print("   로그 파일을 확인하세요: data/crawler.log")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n중단됨. 사용자가 프로그램을 종료했습니다.")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("   상세 내용은 로그 파일을 확인하세요: data/crawler.log")
        sys.exit(1)


if __name__ == "__main__":
    main()
