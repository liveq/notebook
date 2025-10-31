"""
중고나라 크롤러 (Playwright 기반)

참고:
- 중고나라는 네이버 카페로 운영되며, 로그인이 필요할 수 있습니다.
- robots.txt를 준수하며, 과도한 요청을 하지 않습니다.
"""
import re
from typing import List, Dict, Any
from urllib.parse import urljoin, quote
from crawlers.base_crawler import BaseCrawler


class JoonggonaraCrawler(BaseCrawler):
    """중고나라 크롤러 (Playwright)"""

    def __init__(self):
        super().__init__("중고나라")
        self.base_url = "https://cafe.naver.com/joonggonara"

    def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        중고나라에서 키워드 검색

        Args:
            keywords: 검색 키워드 리스트

        Returns:
            검색 결과 리스트
        """
        all_results = []

        # 브라우저 시작
        self.start_browser()

        try:
            for keyword in keywords:
                try:
                    self.logger.info(f"중고나라 검색: {keyword}")
                    results = self._search_keyword(keyword)
                    all_results.extend(results)

                    if len(all_results) >= self.settings['max_results_per_site']:
                        break

                except Exception as e:
                    self.logger.error(f"중고나라 검색 실패 [{keyword}]: {e}")
                    continue

        finally:
            # 브라우저 종료
            self.close_browser()

        # 중복 제거 (URL 기준)
        unique_results = self._remove_duplicates(all_results)
        self.log_result(len(unique_results))

        return unique_results[:self.settings['max_results_per_site']]

    def _search_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        단일 키워드 검색

        Args:
            keyword: 검색 키워드

        Returns:
            검색 결과 리스트
        """
        results = []

        try:
            # 네이버 검색 사용 (중고나라 카페 내 검색)
            search_url = f"https://search.naver.com/search.naver?where=article&query=중고나라+{quote(keyword)}"

            self.logger.info(f"검색 URL: {search_url}")

            # 페이지 이동
            self.goto(search_url, wait_for='networkidle')

            # HTML 파싱
            html = self.get_page_content()
            soup = self.parse_html(html)

            # 검색 결과 파싱
            articles = soup.select('.api_subject_bx')

            for article in articles[:10]:  # 상위 10개만
                try:
                    title_elem = article.select_one('.api_txt_lines.total_tit')
                    link_elem = article.find('a')

                    if not title_elem or not link_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    href = link_elem.get('href', '')

                    if not href or '중고나라' not in href:
                        continue

                    # 매물 정보 추출
                    item = self.create_item(
                        title=title,
                        url=href,
                        description=title,
                        location="중고나라"
                    )

                    results.append(item)

                except Exception as e:
                    self.logger.error(f"중고나라 아이템 파싱 실패: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"중고나라 검색 요청 실패: {e}")

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
