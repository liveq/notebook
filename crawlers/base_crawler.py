"""
기본 크롤러 클래스 (Playwright 기반)
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup
from config import CRAWLER_SETTINGS


class BaseCrawler(ABC):
    """모든 크롤러의 기본 클래스 (Playwright 사용)"""

    def __init__(self, source_name: str):
        """
        Args:
            source_name: 크롤러 소스 이름 (예: "중고나라", "번개장터")
        """
        self.source_name = source_name
        self.settings = CRAWLER_SETTINGS
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # 로깅 설정
        self.logger = logging.getLogger(f"Crawler.{source_name}")

    def __enter__(self):
        """Context manager 진입"""
        self.start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close_browser()

    def start_browser(self):
        """Playwright 브라우저 시작"""
        try:
            self.playwright = sync_playwright().start()

            # 헤드리스 모드로 Chromium 브라우저 실행
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )

            # 컨텍스트 생성 (쿠키, 세션 관리)
            self.context = self.browser.new_context(
                user_agent=self.settings['user_agent'],
                viewport={'width': 1920, 'height': 1080},
                locale='ko-KR',
                timezone_id='Asia/Seoul'
            )

            # 페이지 생성
            self.page = self.context.new_page()

            # JavaScript로 webdriver 감지 우회
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            self.logger.info(f"{self.source_name} 브라우저 시작됨")

        except Exception as e:
            self.logger.error(f"브라우저 시작 실패: {e}")
            raise

    def close_browser(self):
        """브라우저 종료"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info(f"{self.source_name} 브라우저 종료됨")
        except Exception as e:
            self.logger.error(f"브라우저 종료 실패: {e}")

    def goto(self, url: str, wait_for: str = 'load') -> Page:
        """
        URL로 이동

        Args:
            url: 이동할 URL
            wait_for: 대기 조건 ('load', 'networkidle', 'domcontentloaded')

        Returns:
            Page 객체
        """
        try:
            time.sleep(self.settings['delay_between_requests'])

            self.page.goto(url, wait_until=wait_for, timeout=self.settings['timeout'] * 1000)

            # 추가 대기 (안정성)
            time.sleep(1)

            return self.page

        except Exception as e:
            self.logger.error(f"페이지 이동 실패 [{url}]: {e}")
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

    def get_page_content(self) -> str:
        """현재 페이지의 HTML 내용 가져오기"""
        return self.page.content()

    def wait_for_selector(self, selector: str, timeout: int = None):
        """CSS 선택자가 나타날 때까지 대기"""
        timeout_ms = (timeout or self.settings['timeout']) * 1000
        try:
            self.page.wait_for_selector(selector, timeout=timeout_ms)
        except Exception as e:
            self.logger.warning(f"선택자 대기 타임아웃 [{selector}]: {e}")

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
            "date": kwargs.get("date", datetime.now().strftime("%Y-%m-%d")),
            "timestamp": datetime.now().isoformat(),
            "specs": kwargs.get("specs", {}),
            "is_new": kwargs.get("is_new", True),
            "raw_data": kwargs.get("raw_data", {})
        }

    def log_result(self, result_count: int):
        """
        검색 결과 로깅

        Args:
            result_count: 검색 결과 수
        """
        self.logger.info(f"[{self.source_name}] {result_count}개 매물 발견")
