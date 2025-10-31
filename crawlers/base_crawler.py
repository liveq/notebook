"""
기본 크롤러 클래스
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from config import CRAWLER_SETTINGS


class BaseCrawler(ABC):
    """모든 크롤러의 기본 클래스"""

    def __init__(self, source_name: str):
        """
        Args:
            source_name: 크롤러 소스 이름 (예: "중고나라", "번개장터")
        """
        self.source_name = source_name
        self.settings = CRAWLER_SETTINGS
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.settings['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

        # 로깅 설정
        self.logger = logging.getLogger(f"Crawler.{source_name}")

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        HTTP GET 요청

        Args:
            url: 요청 URL
            **kwargs: requests.get()에 전달할 추가 파라미터

        Returns:
            Response 객체
        """
        try:
            time.sleep(self.settings['delay_between_requests'])
            response = self.session.get(
                url,
                timeout=self.settings['timeout'],
                **kwargs
            )
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"GET 요청 실패 [{url}]: {e}")
            raise

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        HTML 파싱

        Args:
            html: HTML 문자열

        Returns:
            BeautifulSoup 객체
        """
        return BeautifulSoup(html, 'html.parser')

    @abstractmethod
    def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        키워드로 검색 (각 크롤러에서 구현 필요)

        Args:
            keywords: 검색 키워드 리스트

        Returns:
            검색 결과 리스트
        """
        pass

    def create_item(self, title: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        표준 매물 아이템 생성

        Args:
            title: 매물 제목
            url: 매물 URL
            **kwargs: 추가 정보 (description, price, location 등)

        Returns:
            매물 정보 딕셔너리
        """
        return {
            "source": self.source_name,
            "title": title,
            "url": url,
            "description": kwargs.get("description", ""),
            "price": kwargs.get("price", ""),
            "location": kwargs.get("location", ""),
            "timestamp": datetime.now().isoformat(),
            "raw_data": kwargs.get("raw_data", {})
        }

    def log_result(self, result_count: int):
        """
        검색 결과 로깅

        Args:
            result_count: 검색 결과 수
        """
        self.logger.info(f"[{self.source_name}] {result_count}개 매물 발견")
