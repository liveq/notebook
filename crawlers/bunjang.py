"""
번개장터 크롤러 (Playwright 기반)
"""
import re
from typing import List, Dict, Any
from urllib.parse import quote
from crawlers.base_crawler import BaseCrawler


class BunjangCrawler(BaseCrawler):
    """번개장터 크롤러 (Playwright)"""

    def __init__(self):
        super().__init__("번개장터")
        self.base_url = "https://m.bunjang.co.kr"

    def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        번개장터에서 키워드 검색

        Args:
            keywords: 검색 키워드 리스트

        Returns:
            검색 결과 리스트
        """
        all_results = []

        # 브라우저 시작
        self.start_browser()

        try:
            for keyword in keywords[:5]:  # 처음 5개 키워드만
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
        단일 키워드 검색

        Args:
            keyword: 검색 키워드

        Returns:
            검색 결과 리스트
        """
        results = []

        try:
            search_url = f"{self.base_url}/search/products?q={quote(keyword)}"

            self.logger.info(f"검색 URL: {search_url}")

            # 페이지 이동
            self.goto(search_url, wait_for='networkidle')

            # 잠시 대기 (동적 로딩)
            self.page.wait_for_timeout(2000)

            # HTML 파싱
            html = self.get_page_content()
            soup = self.parse_html(html)

            # 검색 결과 파싱 (번개장터는 구조가 자주 변경될 수 있음)
            items = soup.select('div[class*="ProductList"] a')

            for item in items[:10]:
                try:
                    title_elem = item.select_one('[class*="ProductCard_name"]')
                    price_elem = item.select_one('[class*="ProductCard_price"]')
                    href = item.get('href', '')

                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    price = price_elem.get_text(strip=True) if price_elem else ""

                    # 절대 URL 생성
                    if href.startswith('/'):
                        url = f"https://m.bunjang.co.kr{href}"
                    else:
                        url = href

                    # 매물 정보 생성
                    result_item = self.create_item(
                        title=title,
                        url=url,
                        price=price,
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
