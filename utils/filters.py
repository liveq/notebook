"""
매물 필터링 및 검증 로직
"""
import re
from typing import Dict, List, Any, Optional
from config import SEARCH_CONDITIONS


class NotebookFilter:
    """노트북 매물 필터링 클래스"""

    def __init__(self):
        self.conditions = SEARCH_CONDITIONS

    def extract_price(self, text: str) -> Optional[int]:
        """
        텍스트에서 가격 추출

        Args:
            text: 가격이 포함된 텍스트

        Returns:
            추출된 가격 (원 단위), 없으면 None
        """
        # 가격 패턴: 숫자 + 만원, 숫자 + 원
        patterns = [
            r'(\d+)\s*만\s*원',  # 40만원, 40 만원
            r'(\d+)\s*만',  # 40만
            r'(\d{3,})\s*원',  # 400000원
            r'(\d{1,3}(?:,\d{3})+)',  # 400,000
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1).replace(',', '')
                price = int(price_str)

                # 만원 단위인 경우 10000을 곱함
                if '만' in match.group(0):
                    price *= 10000

                return price

        return None

    def extract_ram(self, text: str) -> Optional[int]:
        """
        텍스트에서 RAM 용량 추출

        Args:
            text: RAM 정보가 포함된 텍스트

        Returns:
            RAM 용량 (GB), 없으면 None
        """
        # RAM 패턴: 16GB, 16G, 메모리 16
        patterns = [
            r'(\d+)\s*gb',
            r'(\d+)\s*g(?:\s|$|,)',
            r'ram\s*(\d+)',
            r'메모리\s*(\d+)',
        ]

        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))

        return None

    def extract_cpu(self, text: str) -> Optional[Dict[str, Any]]:
        """
        텍스트에서 CPU 정보 추출

        Args:
            text: CPU 정보가 포함된 텍스트

        Returns:
            CPU 정보 딕셔너리 {"type": "i5", "generation": 8}, 없으면 None
        """
        text_lower = text.lower()

        # CPU 패턴: i5-8265u, i5 8세대, i7-10710u 등
        patterns = [
            r'(i[357])[- ](\d{1,2})(?:\d{2,3})',  # i5-8265, i7-10710
            r'(i[357])\s*(\d{1,2})\s*세대',  # i5 8세대
            r'(i[357])[- ](\d)th',  # i5-8th
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                cpu_type = match.group(1)
                generation = int(match.group(2))

                # 세대 수정: 8265 -> 8세대
                if generation > 20:
                    generation = generation // 1000

                return {
                    "type": cpu_type,
                    "generation": generation
                }

        return None

    def check_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        텍스트에 키워드가 포함되어 있는지 확인

        Args:
            text: 검사할 텍스트
            keywords: 확인할 키워드 리스트

        Returns:
            하나라도 포함되어 있으면 True
        """
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
        return False

    def check_negative_keywords(self, text: str) -> bool:
        """
        부정 키워드가 포함되어 있는지 확인

        Args:
            text: 검사할 텍스트

        Returns:
            부정 키워드가 있으면 True
        """
        return self.check_keywords(text, self.conditions["negative_keywords"])

    def validate_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        매물이 조건을 만족하는지 검증

        Args:
            item: 매물 정보 딕셔너리

        Returns:
            검증 결과와 매칭된 키워드를 포함한 딕셔너리
        """
        result = {
            "valid": False,
            "reasons": [],
            "matched_keywords": [],
            "specs": {}
        }

        title = item.get("title", "")
        description = item.get("description", "")
        full_text = f"{title} {description}"

        # 1. 부정 키워드 체크
        if self.check_negative_keywords(full_text):
            result["reasons"].append("부정 키워드 포함")
            return result

        # 2. 가격 체크
        price = self.extract_price(full_text)
        if price:
            result["specs"]["price"] = price
            if not (self.conditions["min_price"] <= price <= self.conditions["max_price"]):
                result["reasons"].append(f"가격 범위 초과: {price:,}원")
                return result
        else:
            # 가격 정보 없으면 일단 통과
            result["specs"]["price"] = None

        # 3. RAM 체크
        ram = self.extract_ram(full_text)
        if ram:
            result["specs"]["ram"] = ram
            if ram < self.conditions["min_ram"]:
                result["reasons"].append(f"RAM 부족: {ram}GB")
                return result
        else:
            # RAM 정보 없으면 일단 통과
            result["specs"]["ram"] = None

        # 4. CPU 체크
        cpu = self.extract_cpu(full_text)
        if cpu:
            result["specs"]["cpu"] = f"{cpu['type']}-{cpu['generation']}세대"
            cpu_type = cpu["type"]
            generation = cpu["generation"]

            if cpu_type in self.conditions["cpu_generations"]:
                valid_gens = self.conditions["cpu_generations"][cpu_type]
                if generation not in valid_gens:
                    result["reasons"].append(f"CPU 세대 미달: {cpu['type']}-{generation}세대")
                    return result
            else:
                # i3나 다른 CPU는 제외
                result["reasons"].append(f"지원하지 않는 CPU: {cpu_type}")
                return result
        else:
            # CPU 정보 없으면 일단 통과
            result["specs"]["cpu"] = None

        # 5. 필수 키워드 체크 (convertible, thunderbolt, lte)
        all_matched = True
        for category, keywords in self.conditions["required_keywords"].items():
            if self.check_keywords(full_text, keywords):
                # 매칭된 키워드 찾기
                for keyword in keywords:
                    if keyword.lower() in full_text.lower():
                        result["matched_keywords"].append(keyword)
            else:
                result["reasons"].append(f"{category} 키워드 미포함")
                all_matched = False

        if not all_matched:
            return result

        # 모든 조건 통과
        result["valid"] = True
        result["reasons"].append("모든 조건 만족")

        return result

    def filter_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        매물 리스트를 필터링

        Args:
            items: 매물 리스트

        Returns:
            필터링된 매물 리스트 (검증 정보 포함)
        """
        filtered_items = []

        for item in items:
            validation = self.validate_item(item)

            if validation["valid"]:
                # 검증 정보를 item에 추가
                item["validation"] = validation
                item["matched_keywords"] = validation["matched_keywords"]
                item["specs"] = validation["specs"]
                filtered_items.append(item)

        return filtered_items
