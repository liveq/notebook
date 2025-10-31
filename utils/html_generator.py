"""
모바일 최적화 HTML 생성
"""
from datetime import datetime
from typing import List, Dict, Any


class HTMLGenerator:
    """검색 결과 HTML 생성 클래스"""

    def __init__(self):
        pass

    def generate_html(self, results: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
        """
        검색 결과를 HTML로 변환

        Args:
            results: 검색 결과 리스트
            stats: 통계 정보

        Returns:
            HTML 문자열
        """
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>중고 노트북 LTE 매물 검색 결과</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}

        .header .stats {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .controls {{
            padding: 15px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 8px 16px;
            border: 1px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}

        .btn:hover {{
            background: #667eea;
            color: white;
        }}

        .btn.active {{
            background: #667eea;
            color: white;
        }}

        .container {{
            padding: 15px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .card.new {{
            border-left: 4px solid #4caf50;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }}

        .card-title {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
            flex: 1;
            line-height: 1.4;
        }}

        .badge {{
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
        }}

        .badge.new {{
            background: #4caf50;
            color: white;
        }}

        .badge.source {{
            background: #e3f2fd;
            color: #1976d2;
        }}

        .card-price {{
            font-size: 20px;
            font-weight: 700;
            color: #667eea;
            margin: 10px 0;
        }}

        .card-info {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }}

        .info-item {{
            background: #f5f5f5;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 13px;
            color: #666;
        }}

        .keywords {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin: 10px 0;
        }}

        .keyword {{
            background: #fff3e0;
            color: #f57c00;
            padding: 3px 8px;
            border-radius: 8px;
            font-size: 12px;
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #f0f0f0;
        }}

        .location {{
            font-size: 13px;
            color: #999;
        }}

        .link-btn {{
            padding: 8px 16px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 20px;
            font-size: 13px;
            transition: background 0.3s;
        }}

        .link-btn:hover {{
            background: #5568d3;
        }}

        .empty {{
            text-align: center;
            padding: 40px 20px;
            color: #999;
        }}

        .timestamp {{
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 13px;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 20px;
            }}

            .card-title {{
                font-size: 15px;
            }}

            .card-price {{
                font-size: 18px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🖥️ 중고 노트북 LTE 매물</h1>
        <div class="stats">
            총 {stats['total_count']}개 매물 | 신규 {stats['new_count']}개
            {self._format_price_range(stats)}
        </div>
    </div>

    <div class="controls">
        <button class="btn active" onclick="sortBy('latest')">최신순</button>
        <button class="btn" onclick="sortBy('price_low')">가격 낮은순</button>
        <button class="btn" onclick="sortBy('price_high')">가격 높은순</button>
        <button class="btn" onclick="filterNew()">신규만 보기</button>
        <button class="btn" onclick="showAll()">전체 보기</button>
    </div>

    <div class="container" id="results">
        {self._generate_cards(results)}
    </div>

    <div class="timestamp">
        검색 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>

    <script>
        let allResults = {self._results_to_json(results)};
        let currentResults = [...allResults];

        function renderResults(results) {{
            const container = document.getElementById('results');
            if (results.length === 0) {{
                container.innerHTML = '<div class="empty">조건에 맞는 매물이 없습니다.</div>';
                return;
            }}

            container.innerHTML = results.map(item => createCard(item)).join('');
        }}

        function createCard(item) {{
            const newBadge = item.is_new ? '<span class="badge new">NEW</span>' : '';
            const price = item.specs.price ? `{self._format_price_js()}` : '가격 문의';
            const specs = item.specs;
            const cpu = specs.cpu || '정보 없음';
            const ram = specs.ram ? specs.ram + 'GB' : '정보 없음';
            const keywords = item.matched_keywords.map(k => `<span class="keyword">${{k}}</span>`).join('');
            const location = item.location || '위치 정보 없음';

            return `
                <div class="card ${{item.is_new ? 'new' : ''}}">
                    <div class="card-header">
                        <div class="card-title">${{item.title}}</div>
                        ${{newBadge}}
                        <span class="badge source">${{item.source}}</span>
                    </div>
                    <div class="card-price">${{price}}</div>
                    <div class="card-info">
                        <div class="info-item">💻 ${{cpu}}</div>
                        <div class="info-item">🧠 ${{ram}}</div>
                    </div>
                    <div class="keywords">${{keywords}}</div>
                    <div class="card-footer">
                        <div class="location">📍 ${{location}}</div>
                        <a href="${{item.url}}" target="_blank" class="link-btn">상세보기</a>
                    </div>
                </div>
            `;
        }}

        function sortBy(type) {{
            // 버튼 활성화 표시
            document.querySelectorAll('.controls .btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');

            switch(type) {{
                case 'latest':
                    currentResults.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                    break;
                case 'price_low':
                    currentResults.sort((a, b) => {{
                        const priceA = a.specs.price || Infinity;
                        const priceB = b.specs.price || Infinity;
                        return priceA - priceB;
                    }});
                    break;
                case 'price_high':
                    currentResults.sort((a, b) => {{
                        const priceA = a.specs.price || 0;
                        const priceB = b.specs.price || 0;
                        return priceB - priceA;
                    }});
                    break;
            }}
            renderResults(currentResults);
        }}

        function filterNew() {{
            currentResults = allResults.filter(item => item.is_new);
            renderResults(currentResults);
        }}

        function showAll() {{
            currentResults = [...allResults];
            renderResults(currentResults);
        }}
    </script>
</body>
</html>
"""
        return html

    def _format_price_range(self, stats: Dict[str, Any]) -> str:
        """가격 범위 포맷팅"""
        price_range = stats.get("price_range", {})
        min_price = price_range.get("min")
        max_price = price_range.get("max")

        if min_price and max_price:
            return f" | 가격대 {min_price//10000}만원~{max_price//10000}만원"
        return ""

    def _format_price_js(self) -> str:
        """JavaScript용 가격 포맷팅 코드"""
        return "item.specs.price ? (item.specs.price >= 10000 ? Math.floor(item.specs.price/10000) + '만원' : item.specs.price + '원') : '가격 문의'"

    def _generate_cards(self, results: List[Dict[str, Any]]) -> str:
        """카드 HTML 생성"""
        if not results:
            return '<div class="empty">조건에 맞는 매물이 없습니다.</div>'

        cards = []
        for item in results:
            new_badge = '<span class="badge new">NEW</span>' if item.get("is_new") else ""
            price = self._format_price(item.get("specs", {}).get("price"))
            specs = item.get("specs", {})
            cpu = specs.get("cpu") or "정보 없음"
            ram = f"{specs.get('ram')}GB" if specs.get("ram") else "정보 없음"
            keywords = "".join([f'<span class="keyword">{k}</span>' for k in item.get("matched_keywords", [])])
            location = item.get("location") or "위치 정보 없음"

            card = f"""
                <div class="card {'new' if item.get('is_new') else ''}">
                    <div class="card-header">
                        <div class="card-title">{item.get('title', '제목 없음')}</div>
                        {new_badge}
                        <span class="badge source">{item.get('source', 'unknown')}</span>
                    </div>
                    <div class="card-price">{price}</div>
                    <div class="card-info">
                        <div class="info-item">💻 {cpu}</div>
                        <div class="info-item">🧠 {ram}</div>
                    </div>
                    <div class="keywords">{keywords}</div>
                    <div class="card-footer">
                        <div class="location">📍 {location}</div>
                        <a href="{item.get('url', '#')}" target="_blank" class="link-btn">상세보기</a>
                    </div>
                </div>
            """
            cards.append(card)

        return "\n".join(cards)

    def _format_price(self, price: int) -> str:
        """가격 포맷팅"""
        if not price:
            return "가격 문의"
        if price >= 10000:
            return f"{price//10000}만원"
        return f"{price:,}원"

    def _results_to_json(self, results: List[Dict[str, Any]]) -> str:
        """결과를 JSON 문자열로 변환 (JavaScript용)"""
        import json
        return json.dumps(results, ensure_ascii=False)

    def save_html(self, results: List[Dict[str, Any]], stats: Dict[str, Any], output_path: str) -> bool:
        """
        HTML 파일로 저장

        Args:
            results: 검색 결과
            stats: 통계 정보
            output_path: 출력 파일 경로

        Returns:
            저장 성공 여부
        """
        try:
            html = self.generate_html(results, stats)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"HTML 저장 중 오류 발생: {e}")
            return False
