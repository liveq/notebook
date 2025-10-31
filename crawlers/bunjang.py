"""
번개장터 크롤러 (네이버 통합 검색 기반)
"""
from typing import List, Dict, Any
from urllib.parse import quote
from crawlers.base_crawler import BaseCrawler


class BunjangCrawler(BaseCrawler):
    """번개장터 크롤러 (네이버 통합 검색 기반)"""

    def __init__(self):
        super().__init__("번개장터")
        self.base_url = "https://search.naver.com"

    def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        네이버 통합 검색에서 번개장터 관련 결과 검색

        Args:
            keywords: 검색 키워드 리스트

        Returns:
            검색 결과 리스트
        """
        all_results = []

        # 브라우저 시작
        self.start_browser()

        try:
            for keyword in keywords[:10]:  # 처음 10개 키워드만
                try:
                    self.logger.info(f"번개장터 검색: {keyword}")
                    results = self._search_keyword(keyword)
                    all_results.extend(results)

                    if len(all_results) >= self.settings['max_results_per_site']:
                        break

                except Exception as e:
                    self.logger.error(f"번개장터 검색 실패 [{keyword}]: {e}")
                    continue

        finally:
            # 브라우저 종료
            self.close_browser()

        # 중복 제거
        unique_results = self._remove_duplicates(all_results)
        self.log_result(len(unique_results))

        return unique_results[:self.settings['max_results_per_site']]

    def _search_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        단일 키워드로 네이버 통합 검색

        Args:
            keyword: 검색 키워드

        Returns:
            검색 결과 리스트
        """
        results = []

        try:
            # 네이버 통합 검색: "번개장터 + 키워드"
            search_query = f"번개장터 {keyword}"
            search_url = f"{self.base_url}/search.naver?where=nexearch&query={quote(search_query)}"

            self.logger.info(f"검색 URL: {search_url}")

            # 페이지 이동
            self.goto(search_url, wait_for='networkidle')

            # 잠시 대기
            self.page.wait_for_timeout(1000)

            # HTML 파싱
            html = self.get_page_content()
            soup = self.parse_html(html)

            # 검색 결과 추출
            links = soup.select('a[href*="bunjang"]')

            for link in links[:10]:
                try:
                    href = link.get('href', '')
                    if not href or 'bunjang.co.kr' not in href:
                        continue

                    # 제목 추출
                    title = link.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue

                    # 매물 정보 생성
                    result_item = self.create_item(
                        title=title,
                        url=href,
                        description=title,
                        location="번개장터"
                    )

                    results.append(result_item)

                except Exception as e:
                    self.logger.error(f"번개장터 아이템 파싱 실패: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"번개장터 검색 요청 실패: {e}")

        return results

    def _remove_duplicates(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """URL 기준 중복 제거"""
        seen_urls = set()
        unique_items = []

        for item in items:
            url = item.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)

        return unique_items
