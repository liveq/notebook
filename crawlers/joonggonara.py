"""
중고나라 크롤러 (네이버 통합 검색 기반)

네이버 통합 검색에서 중고나라 관련 결과를 수집합니다.
직접 카페 접근 대신 네이버 검색 결과를 활용하여 로그인 없이 사용 가능합니다.
"""
import re
from typing import List, Dict, Any
from urllib.parse import quote
from crawlers.base_crawler import BaseCrawler


class JoonggonaraCrawler(BaseCrawler):
    """중고나라 크롤러 (네이버 통합 검색 기반)"""

    def __init__(self):
        super().__init__("중고나라")
        self.base_url = "https://search.naver.com"

    def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        네이버 통합 검색에서 중고나라 관련 결과 검색

        Args:
            keywords: 검색 키워드 리스트

        Returns:
            검색 결과 리스트
        """
        all_results = []

        # 브라우저 시작
        self.start_browser()

        try:
            # 키워드 수 제한 (너무 많으면 느림)
            for keyword in keywords[:10]:
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
        단일 키워드로 네이버 통합 검색

        Args:
            keyword: 검색 키워드

        Returns:
            검색 결과 리스트
        """
        results = []

        try:
            # 네이버 통합 검색: "중고나라 + 키워드"
            search_query = f"중고나라 {keyword}"
            search_url = f"{self.base_url}/search.naver?where=article&query={quote(search_query)}"

            self.logger.info(f"검색 URL: {search_url}")

            # 페이지 이동
            self.goto(search_url, wait_for='networkidle')

            # 잠시 대기
            self.page.wait_for_timeout(1000)

            # HTML 파싱
            html = self.get_page_content()
            soup = self.parse_html(html)

            # 검색 결과 추출
            # 네이버 카페 검색 결과 선택자
            articles = soup.select('.api_subject_bx')

            for article in articles[:15]:  # 상위 15개
                try:
                    # 제목 추출
                    title_elem = article.select_one('.api_txt_lines')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # URL 추출
                    link_elem = article.find('a')
                    if not link_elem:
                        continue

                    href = link_elem.get('href', '')

                    # 중고나라 링크만 필터링
                    if not href or 'joonggonara' not in href:
                        continue

                    # 설명 추출 (있으면)
                    desc_elem = article.select_one('.dsc_txt_wrap')
                    description = desc_elem.get_text(strip=True) if desc_elem else title

                    # 매물 정보 생성
                    item = self.create_item(
                        title=title,
                        url=href,
                        description=description,
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
