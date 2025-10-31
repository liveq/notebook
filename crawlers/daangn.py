"""
당근마켓 크롤러 (Playwright 기반)
"""
import re
from typing import List, Dict, Any
from urllib.parse import quote
from crawlers.base_crawler import BaseCrawler


class DaangnCrawler(BaseCrawler):
    """당근마켓 크롤러 (Playwright)"""

    def __init__(self):
        super().__init__("당근마켓")
        self.base_url = "https://www.daangn.com"

    def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        당근마켓에서 키워드 검색

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
                    self.logger.info(f"당근마켓 검색: {keyword}")
                    results = self._search_keyword(keyword)
                    all_results.extend(results)

                    if len(all_results) >= self.settings['max_results_per_site']:
                        break

                except Exception as e:
                    self.logger.error(f"당근마켓 검색 실패 [{keyword}]: {e}")
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
            search_url = f"{self.base_url}/search/{quote(keyword)}"

            self.logger.info(f"검색 URL: {search_url}")

            # 페이지 이동
            self.goto(search_url, wait_for='networkidle')

            # 잠시 대기 (동적 로딩)
            self.page.wait_for_timeout(2000)

            # HTML 파싱
            html = self.get_page_content()
            soup = self.parse_html(html)

            # 검색 결과 파싱
            articles = soup.select('article[class*="card"]')

            for article in articles[:10]:
                try:
                    title_elem = article.select_one('[class*="title"]')
                    price_elem = article.select_one('[class*="price"]')
                    link_elem = article.find('a')

                    if not title_elem or not link_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    price = price_elem.get_text(strip=True) if price_elem else ""
                    href = link_elem.get('href', '')

                    # 절대 URL 생성
                    if href.startswith('/'):
                        url = f"{self.base_url}{href}"
                    else:
                        url = href

                    # 위치 추출
                    location_elem = article.select_one('[class*="region"]')
                    location = location_elem.get_text(strip=True) if location_elem else ""

                    # 매물 정보 생성
                    result_item = self.create_item(
                        title=title,
                        url=url,
                        price=price,
                        location=location,
                        description=title
                    )

                    results.append(result_item)

                except Exception as e:
                    self.logger.error(f"당근마켓 아이템 파싱 실패: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"당근마켓 검색 요청 실패: {e}")

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
