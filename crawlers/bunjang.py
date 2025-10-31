"""
번개장터 크롤러

참고:
- 번개장터는 앱 기반 서비스이며, API 접근이 제한될 수 있습니다.
- robots.txt를 준수하며, 과도한 요청을 하지 않습니다.
- 실제 사용 시 번개장터 정책을 확인하세요.
"""
import re
import json
from typing import List, Dict, Any
from urllib.parse import quote
from crawlers.base_crawler import BaseCrawler


class BunjangCrawler(BaseCrawler):
    """번개장터 크롤러"""

    def __init__(self):
        super().__init__("번개장터")
        self.base_url = "https://www.bunjang.co.kr"
        self.api_base = "https://api.bunjang.co.kr"

    def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        번개장터에서 키워드 검색

        Args:
            keywords: 검색 키워드 리스트

        Returns:
            검색 결과 리스트
        """
        all_results = []

        for keyword in keywords:
            try:
                self.logger.info(f"번개장터 검색: {keyword}")
                results = self._search_keyword(keyword)
                all_results.extend(results)

                if len(all_results) >= self.settings['max_results_per_site']:
                    break

            except Exception as e:
                self.logger.error(f"번개장터 검색 실패 [{keyword}]: {e}")
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
            # 번개장터 검색 URL
            search_url = f"{self.base_url}/search/products?q={quote(keyword)}"

            response = self.get(search_url)
            soup = self.parse_html(response.text)

            # 검색 결과 파싱
            # 번개장터는 동적 렌더링을 사용할 수 있어 selenium이 필요할 수 있음
            # 여기서는 기본 HTML 파싱을 시도합니다.

            # 상품 카드 선택 (실제 클래스명은 다를 수 있음)
            products = soup.select('div[class*="product"]')[:20]

            for product in products:
                try:
                    # 제목 추출
                    title_elem = product.select_one('a[class*="title"], div[class*="name"]')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # URL 추출
                    link_elem = product.select_one('a')
                    if not link_elem or not link_elem.get('href'):
                        continue

                    product_url = link_elem.get('href')
                    if not product_url.startswith('http'):
                        product_url = self.base_url + product_url

                    # 가격 추출
                    price_elem = product.select_one('[class*="price"]')
                    price = price_elem.get_text(strip=True) if price_elem else ""

                    # 위치 추출
                    location_elem = product.select_one('[class*="location"], [class*="region"]')
                    location = location_elem.get_text(strip=True) if location_elem else ""

                    # 매물 생성
                    item = self.create_item(
                        title=title,
                        url=product_url,
                        price=price,
                        location=location
                    )

                    results.append(item)

                except Exception as e:
                    self.logger.error(f"번개장터 아이템 파싱 실패: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"번개장터 검색 요청 실패: {e}")

        return results

    def _search_via_api(self, keyword: str) -> List[Dict[str, Any]]:
        """
        API를 통한 검색 (실제 API 엔드포인트가 다를 수 있음)

        Args:
            keyword: 검색 키워드

        Returns:
            검색 결과 리스트
        """
        results = []

        try:
            # API 요청 (실제 엔드포인트는 다를 수 있음)
            api_url = f"{self.api_base}/search/products"
            params = {
                "order": "date",
                "q": keyword,
                "page": 0,
                "req_ref": "search"
            }

            response = self.get(api_url, params=params)
            data = response.json()

            # 응답 파싱
            products = data.get("list", [])

            for product in products[:20]:
                try:
                    item = self.create_item(
                        title=product.get("name", ""),
                        url=f"{self.base_url}/products/{product.get('pid')}",
                        description=product.get("description", ""),
                        price=str(product.get("price", "")),
                        location=product.get("location", ""),
                        raw_data=product
                    )

                    results.append(item)

                except Exception as e:
                    self.logger.error(f"번개장터 API 응답 파싱 실패: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"번개장터 API 요청 실패: {e}")

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

    def get_product_detail(self, url: str) -> Dict[str, Any]:
        """
        상품 상세 정보 가져오기

        Args:
            url: 상품 URL

        Returns:
            상세 정보 딕셔너리
        """
        try:
            response = self.get(url)
            soup = self.parse_html(response.text)

            # 상품 설명 추출
            desc_elem = soup.select_one('[class*="description"], [class*="content"]')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            return {
                "description": description
            }

        except Exception as e:
            self.logger.error(f"상세 정보 추출 실패 [{url}]: {e}")
            return {}
