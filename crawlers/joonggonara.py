"""
중고나라 크롤러

참고:
- 중고나라는 네이버 카페로 운영되며, 로그인이 필요할 수 있습니다.
- robots.txt를 준수하며, 과도한 요청을 하지 않습니다.
- 실제 사용 시 네이버 카페 정책을 확인하세요.
"""
import re
from typing import List, Dict, Any
from urllib.parse import urljoin, quote
from crawlers.base_crawler import BaseCrawler


class JoonggonaraCrawler(BaseCrawler):
    """중고나라 크롤러"""

    def __init__(self):
        super().__init__("중고나라")
        self.base_url = "https://cafe.naver.com/joonggonara"
        # 실제로는 로그인이 필요할 수 있음

    def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        중고나라에서 키워드 검색

        Args:
            keywords: 검색 키워드 리스트

        Returns:
            검색 결과 리스트
        """
        all_results = []

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
            # 중고나라 검색 URL (실제 URL 구조는 다를 수 있음)
            # 네이버 카페 검색은 iframe을 사용하므로 직접 접근이 어려울 수 있음
            search_url = f"https://cafe.naver.com/ArticleSearchList.nhn?search.clubid=10050146&search.searchBy=0&search.query={quote(keyword)}"

            response = self.get(search_url)
            soup = self.parse_html(response.text)

            # 검색 결과 파싱 (실제 구조에 맞게 수정 필요)
            # 네이버 카페는 iframe으로 보호되어 있어 직접 스크래핑이 어려울 수 있음
            # 이 부분은 예시 코드입니다.

            articles = soup.select('.article-board tbody tr')

            for article in articles[:20]:  # 상위 20개만
                try:
                    title_elem = article.select_one('.article-title a')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')

                    # 절대 URL 생성
                    if href:
                        article_url = urljoin(self.base_url, href)
                    else:
                        continue

                    # 매물 정보 추출
                    item = self.create_item(
                        title=title,
                        url=article_url,
                        description="",
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

    def get_article_detail(self, url: str) -> Dict[str, Any]:
        """
        게시글 상세 정보 가져오기

        Args:
            url: 게시글 URL

        Returns:
            상세 정보 딕셔너리
        """
        try:
            response = self.get(url)
            soup = self.parse_html(response.text)

            # 본문 내용 추출 (실제 구조에 맞게 수정 필요)
            content_elem = soup.select_one('.article-content')
            content = content_elem.get_text(strip=True) if content_elem else ""

            # 가격 정보 추출
            price = self._extract_price(content)

            # 위치 정보 추출
            location = self._extract_location(content)

            return {
                "description": content,
                "price": price,
                "location": location
            }

        except Exception as e:
            self.logger.error(f"상세 정보 추출 실패 [{url}]: {e}")
            return {}

    def _extract_price(self, text: str) -> str:
        """텍스트에서 가격 정보 추출"""
        # 가격 패턴 매칭
        patterns = [
            r'(\d+)\s*만\s*원',
            r'(\d+)\s*만',
            r'(\d{3,})\s*원',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return ""

    def _extract_location(self, text: str) -> str:
        """텍스트에서 위치 정보 추출"""
        # 간단한 지역명 추출 (더 정교한 로직 필요)
        regions = ['서울', '경기', '인천', '부산', '대구', '대전', '광주', '울산', '세종']
        for region in regions:
            if region in text:
                return region

        return ""
