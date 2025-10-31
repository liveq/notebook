"""
결과 저장 및 로드 관리
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Set
from config import FILE_PATHS


class ResultStorage:
    """검색 결과 저장 및 관리 클래스"""

    def __init__(self):
        self.results_path = FILE_PATHS["results"]
        self.previous_path = FILE_PATHS["previous_results"]
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """데이터 디렉토리가 없으면 생성"""
        os.makedirs(os.path.dirname(self.results_path), exist_ok=True)

    def save_results(self, results: List[Dict[str, Any]]) -> bool:
        """
        검색 결과 저장

        Args:
            results: 저장할 결과 리스트

        Returns:
            저장 성공 여부
        """
        try:
            # 이전 결과 백업
            if os.path.exists(self.results_path):
                with open(self.results_path, 'r', encoding='utf-8') as f:
                    previous_data = json.load(f)
                with open(self.previous_path, 'w', encoding='utf-8') as f:
                    json.dump(previous_data, f, ensure_ascii=False, indent=2)

            # 새 결과 저장
            data = {
                "timestamp": datetime.now().isoformat(),
                "total_count": len(results),
                "results": results
            }

            with open(self.results_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"결과 저장 중 오류 발생: {e}")
            return False

    def load_results(self) -> List[Dict[str, Any]]:
        """
        저장된 결과 로드

        Returns:
            결과 리스트
        """
        try:
            if os.path.exists(self.results_path):
                with open(self.results_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("results", [])
        except Exception as e:
            print(f"결과 로드 중 오류 발생: {e}")

        return []

    def load_previous_results(self) -> List[Dict[str, Any]]:
        """
        이전 검색 결과 로드

        Returns:
            이전 결과 리스트
        """
        try:
            if os.path.exists(self.previous_path):
                with open(self.previous_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("results", [])
        except Exception as e:
            print(f"이전 결과 로드 중 오류 발생: {e}")

        return []

    def remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        중복 매물 제거 (URL 기준)

        Args:
            results: 결과 리스트

        Returns:
            중복이 제거된 결과 리스트
        """
        seen_urls: Set[str] = set()
        unique_results = []

        for item in results:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(item)

        return unique_results

    def find_new_items(self, current_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        이전 결과와 비교하여 신규 매물 찾기

        Args:
            current_results: 현재 검색 결과

        Returns:
            신규 매물 리스트
        """
        previous_results = self.load_previous_results()
        previous_urls = {item.get("url") for item in previous_results}

        new_items = []
        for item in current_results:
            if item.get("url") not in previous_urls:
                item["is_new"] = True
                new_items.append(item)
            else:
                item["is_new"] = False

        return new_items

    def get_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        검색 결과 통계 생성

        Args:
            results: 결과 리스트

        Returns:
            통계 정보 딕셔너리
        """
        stats = {
            "total_count": len(results),
            "new_count": sum(1 for item in results if item.get("is_new", False)),
            "by_source": {},
            "price_range": {
                "min": None,
                "max": None,
                "avg": None
            }
        }

        # 출처별 통계
        for item in results:
            source = item.get("source", "unknown")
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

        # 가격 통계
        prices = [
            item.get("specs", {}).get("price")
            for item in results
            if item.get("specs", {}).get("price")
        ]

        if prices:
            stats["price_range"]["min"] = min(prices)
            stats["price_range"]["max"] = max(prices)
            stats["price_range"]["avg"] = sum(prices) // len(prices)

        return stats
