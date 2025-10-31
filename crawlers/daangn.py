"""
당근마켓 크롤러

참고:
- 당근마켓은 지역 기반 서비스로, 특정 지역을 선택해야 합니다.
- robots.txt를 준수하며, 과도한 요청을 하지 않습니다.
- 실제 사용 시 당근마켓 정책을 확인하세요.
"""
import re
from typing import List, Dict, Any
from urllib.parse import quote
from crawlers.base_crawler import BaseCrawler


class DaangnCrawler(BaseCrawler):
    """당근마켓 크롤러"""

    def __init__(self, region: str = "전국"):
        """
        Args:
            region: 검색할 지역 (예: "서울", "경기")
        """
        super().__init__("당근마켓")
        self.base_url = "https://www.daangn.com"
        self.region = region

    def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        당근마켓에서 키워드 검색

        Args:
            keywords: 검색 키워드 리스트

        Returns:
            검색 결과 리스트
        """
        all_results = []

        for keyword in keywords:
            try:
                self.logger.info(f"당근마켓 검색: {keyword}")
                results = self._search_keyword(keyword)
                all_results.extend(results)

                if len(all_results) >= self.settings['max_results_per_site']:
                    break

            except Exception as e:
                self.logger.error(f"당근마켓 검색 실패 [{keyword}]: {e}")
                continue

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
            # 당근마켓 검색 URL
            search_url = f"{self.base_url}/search/{quote(keyword)}"

            response = self.get(search_url)
            soup = self.parse_html(response.text)

            # 검색 결과 파싱
            # 당근마켓도 동적 렌더링을 사용할 수 있습니다.

            # 상품 카드 선택 (실제 클래스명은 다를 수 있음)
            articles = soup.select('article[class*="article"], div[class*="article-card"]')[:20]

            for article in articles:
                try:
                    # 제목 추출
                    title_elem = article.select_one('h2, [class*="title"]')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # URL 추출
                    link_elem = article.select_one('a')
                    if not link_elem or not link_elem.get('href'):
                        continue

                    article_url = link_elem.get('href')
                    if not article_url.startswith('http'):
                        article_url = self.base_url + article_url

                    # 가격 추출
                    price_elem = article.select_one('[class*="price"]')
                    price = price_elem.get_text(strip=True) if price_elem else ""

                    # 위치 추출
                    location_elem = article.select_one('[class*="region"], [class*="location"]')
                    location = location_elem.get_text(strip=True) if location_elem else ""

                    # 매물 생성
                    item = self.create_item(
                        title=title,
                        url=article_url,
                        price=price,
                        location=location
                    )

                    results.append(item)

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

            # 상품 설명 추출
            desc_elem = soup.select_one('[id*="article-description"], [class*="content"]')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # 가격 추출
            price_elem = soup.select_one('[id*="article-price"], [class*="price-text"]')
            price = price_elem.get_text(strip=True) if price_elem else ""

            # 위치 추출
            location_elem = soup.select_one('[id*="article-region"], [class*="region-name"]')
            location = location_elem.get_text(strip=True) if location_elem else ""

            return {
                "description": description,
                "price": price,
                "location": location
            }

        except Exception as e:
            self.logger.error(f"상세 정보 추출 실패 [{url}]: {e}")
            return {}
