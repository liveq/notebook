#!/usr/bin/env python3
"""
간단한 구글 검색 테스트 (requests 기반)
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import json
from datetime import datetime

def test_google_search(query):
    """구글 검색 테스트"""
    print(f"\n검색 쿼리: {query}")

    # 구글 검색 URL
    search_url = f"https://www.google.com/search?q={quote(query)}&hl=ko"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8',
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"응답 코드: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 구글 검색 결과 추출
            results = []
            search_results = soup.select('div.g')

            print(f"검색 결과 개수: {len(search_results)}")

            for i, result in enumerate(search_results[:5], 1):
                try:
                    # 제목
                    title_elem = result.select_one('h3')
                    title = title_elem.get_text(strip=True) if title_elem else "제목 없음"

                    # URL
                    link_elem = result.select_one('a')
                    url = link_elem.get('href', '') if link_elem else ""

                    print(f"\n[{i}] {title}")
                    print(f"    URL: {url[:100]}...")

                    results.append({
                        'title': title,
                        'url': url,
                        'source': '구글검색',
                        'description': title,
                        'location': '',
                        'price': '',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'timestamp': datetime.now().isoformat(),
                        'specs': {},
                        'is_new': True
                    })

                except Exception as e:
                    print(f"결과 파싱 오류: {e}")

            return results

        else:
            print(f"검색 실패: HTTP {response.status_code}")
            return []

    except Exception as e:
        print(f"오류 발생: {e}")
        return []

def main():
    print("=" * 60)
    print("구글 검색 테스트")
    print("=" * 60)

    # 테스트 검색
    queries = [
        "중고나라 노트북 LTE",
        "번개장터 노트북 WWAN",
        "당근마켓 2in1 LTE"
    ]

    all_results = []

    for query in queries:
        results = test_google_search(query)
        all_results.extend(results)

    print(f"\n{'=' * 60}")
    print(f"총 수집 결과: {len(all_results)}개")
    print(f"{'=' * 60}")

    # JSON 저장
    output = {
        "results": all_results,
        "stats": {
            "total_count": len(all_results),
            "new_count": len(all_results),
            "last_updated": datetime.now().isoformat()
        }
    }

    with open('/home/user/notebook/data/results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과 저장 완료: /home/user/notebook/data/results.json")

    return len(all_results) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
