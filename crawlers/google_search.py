"""
구글 검색 기반 크롤러

구글 검색 결과에서 중고나라/번개장터/당근마켓 링크를 수집합니다.
실제 사이트 크롤링이 아닌 검색 엔진 결과만 활용합니다.
"""
import re
from typing import List, Dict, Any
from urllib.parse import quote, unquote
from crawlers.base_crawler import BaseCrawler


class GoogleSearchCrawler(BaseCrawler):
    """구글 검색 기반 통합 크롤러"""

    def __init__(self):
        super().__init__("구글검색")
        self.base_url = "https://www.google.com"

    def search_all_platforms(self, keywords: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        모든 플랫폼에서 검색

        Args:
            keywords: 검색 키워드 리스트

        Returns:
            플랫폼별 검색 결과 딕셔너리
        """
        results = {
            "중고나라": [],
            "번개장터": [],
            "당근마켓": []
        }

        # 브라우저 시작
        self.start_browser()

        try:
            # 각 플랫폼별로 검색
            for platform in ["중고나라", "번개장터", "당근마켓"]:
                self.logger.info(f"[{platform}] 검색 시작")

                # 키워드당 검색 (처음 3개만)
                for keyword in keywords[:3]:
                    try:
                        platform_results = self._search_platform_keyword(platform, keyword)
                        results[platform].extend(platform_results)

                        # 플랫폼당 최대 20개
                        if len(results[platform]) >= 20:
                            break

                    except Exception as e:
                        self.logger.error(f"[{platform}] 검색 실패 [{keyword}]: {e}")
                        continue

                # 중복 제거
                results[platform] = self._remove_duplicates(results[platform])
                self.logger.info(f"[{platform}] {len(results[platform])}개 발견")

        finally:
            # 브라우저 종료
            self.close_browser()

        return results

    def _search_platform_keyword(self, platform: str, keyword: str) -> List[Dict[str, Any]]:
        """
        특정 플랫폼 + 키워드로 구글 검색

        Args:
            platform: 플랫폼 이름 (중고나라, 번개장터, 당근마켓)
            keyword: 검색 키워드

        Returns:
            검색 결과 리스트
        """
        results = []

        try:
            # 구글 검색 쿼리
            search_query = f"{platform} {keyword}"
            search_url = f"{self.base_url}/search?q={quote(search_query)}&hl=ko"

            self.logger.info(f"검색: {search_query}")

            # 페이지 이동
            self.goto(search_url, wait_for='networkidle')

            # 잠시 대기
            self.page.wait_for_timeout(2000)

            # HTML 파싱
            html = self.get_page_content()
            soup = self.parse_html(html)

            # 구글 검색 결과 추출
            search_results = soup.select('div.g')

            for result in search_results[:10]:  # 상위 10개
                try:
                    # 제목 추출
                    title_elem = result.select_one('h3')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # URL 추출
                    link_elem = result.select_one('a')
                    if not link_elem:
                        continue

                    href = link_elem.get('href', '')

                    # 플랫폼 도메인 필터링
                    domain_map = {
                        "중고나라": "joonggonara",
                        "번개장터": "bunjang",
                        "당근마켓": "daangn"
                    }

                    if domain_map[platform] not in href:
                        continue

                    # 설명 추출
                    desc_elem = result.select_one('.VwiC3b')
                    description = desc_elem.get_text(strip=True) if desc_elem else title

                    # 매물 정보 생성
                    item = self.create_item(
                        title=title,
                        url=href,
                        description=description,
                        location=platform
                    )

                    # source를 platform 이름으로 설정
                    item['source'] = platform

                    results.append(item)

                except Exception as e:
                    self.logger.error(f"결과 파싱 실패: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"구글 검색 실패: {e}")

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
