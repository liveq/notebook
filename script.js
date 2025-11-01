// 데이터 저장
let allResults = [];
let filteredResults = [];
let currentFilter = 'all';
let currentSort = 'price-asc';

// DOM 요소
const refreshBtn = document.getElementById('refreshBtn');
const resultsBody = document.getElementById('resultsBody');
const noResults = document.getElementById('noResults');
const lastUpdate = document.getElementById('lastUpdate');
const totalCount = document.getElementById('totalCount');
const newCount = document.getElementById('newCount');
const sortSelect = document.getElementById('sortSelect');
const filterBtns = document.querySelectorAll('.filter-btn');

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    loadResults();
    setupEventListeners();
});

// 이벤트 리스너 설정
function setupEventListeners() {
    refreshBtn.addEventListener('click', () => {
        location.reload();
    });

    sortSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        applyFiltersAndSort();
    });

    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            filterBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            applyFiltersAndSort();
        });
    });
}

// 결과 로드
async function loadResults() {
    try {
        const response = await fetch('./data/results.json');

        if (!response.ok) {
            throw new Error('결과 파일을 찾을 수 없습니다');
        }

        const data = await response.json();
        let serverResults = data.results || [];

        // LocalStorage에서 수동 입력 데이터 로드
        const manualItems = JSON.parse(localStorage.getItem('manualItems') || '[]');

        // 수동 입력 데이터 형식 변환 (platform -> source, collected_at -> timestamp)
        const normalizedManualItems = manualItems.map(item => ({
            ...item,
            source: item.platform,
            timestamp: item.collected_at,
            is_manual: true  // 수동 입력 표시
        }));

        // 서버 데이터와 수동 입력 데이터 합치기
        allResults = [...normalizedManualItems, ...serverResults];

        // 통계 업데이트 (수동 입력 포함)
        const combinedStats = {
            total_count: allResults.length,
            new_count: data.stats?.new_count || 0,
            last_updated: data.stats?.last_updated
        };
        updateStats(combinedStats);

        // 결과 표시
        applyFiltersAndSort();

    } catch (error) {
        console.error('데이터 로드 실패:', error);

        // 서버 데이터가 없어도 LocalStorage 데이터는 표시
        const manualItems = JSON.parse(localStorage.getItem('manualItems') || '[]');
        if (manualItems.length > 0) {
            allResults = manualItems.map(item => ({
                ...item,
                source: item.platform,
                timestamp: item.collected_at,
                is_manual: true
            }));
            updateStats({ total_count: allResults.length, new_count: 0 });
            applyFiltersAndSort();
        } else {
            showNoResults();
        }
    }
}

// 통계 업데이트
function updateStats(stats) {
    if (!stats) return;

    totalCount.textContent = stats.total_count || 0;
    newCount.textContent = stats.new_count || 0;

    if (stats.last_updated) {
        const date = new Date(stats.last_updated);
        lastUpdate.textContent = formatDate(date);
    }
}

// 필터 및 정렬 적용
function applyFiltersAndSort() {
    // 필터 적용
    if (currentFilter === 'new') {
        filteredResults = allResults.filter(item => item.is_new);
    } else {
        filteredResults = [...allResults];
    }

    // 정렬 적용
    sortResults();

    // 렌더링
    renderResults();
}

// 정렬
function sortResults() {
    filteredResults.sort((a, b) => {
        if (currentSort === 'price-asc') {
            return parsePrice(a.price) - parsePrice(b.price);
        } else if (currentSort === 'price-desc') {
            return parsePrice(b.price) - parsePrice(a.price);
        } else if (currentSort === 'latest') {
            return new Date(b.date) - new Date(a.date);
        }
        return 0;
    });
}

// 가격 파싱
function parsePrice(priceStr) {
    if (!priceStr) return 0;
    // 숫자만 추출
    const match = priceStr.toString().match(/\d+/g);
    if (!match) return 0;
    return parseInt(match.join(''));
}

// 결과 렌더링
function renderResults() {
    if (filteredResults.length === 0) {
        showNoResults();
        return;
    }

    noResults.style.display = 'none';

    resultsBody.innerHTML = filteredResults.map(item => {
        const conditions = checkConditions(item);
        const conditionsText = `${conditions.passed}/${conditions.total}`;
        const conditionsClass = conditions.passed === conditions.total ? 'all-pass' :
                                conditions.passed > 0 ? 'partial' : 'fail';

        const newBadge = item.is_new ? '<span class="new-badge">NEW</span>' : '';

        return `
            <tr>
                <td>${getPlatformBadge(item.source)}</td>
                <td class="title-cell">
                    ${newBadge}
                    <span class="title-text">${escapeHtml(item.title)}</span>
                </td>
                <td class="price-cell">${formatPrice(item.price)}</td>
                <td>${item.location || '-'}</td>
                <td>${formatDate(item.date)}</td>
                <td><span class="condition-badge ${conditionsClass}">${conditionsText}</span></td>
                <td><a href="${item.url}" target="_blank" class="link-btn">보기</a></td>
                <td class="timestamp-cell">${formatTimestamp(item.timestamp)}</td>
            </tr>
        `;
    }).join('');
}

// 조건 체크
function checkConditions(item) {
    const checks = [
        item.specs?.cpu && validateCPU(item.specs.cpu),
        item.specs?.ram && validateRAM(item.specs.ram),
        item.specs?.lte || checkKeyword(item.description, ['lte', 'wwan', '5g']),
        checkKeyword(item.description, ['360', '2-in-1', '2in1', '컨버터블']),
        checkKeyword(item.description, ['터치', 'touch']),
        checkKeyword(item.description, ['thunderbolt', 'tb3', 'tb4', '썬더볼트'])
    ];

    const passed = checks.filter(c => c).length;
    return { passed, total: checks.length };
}

// CPU 검증
function validateCPU(cpuText) {
    if (!cpuText) return false;
    const text = cpuText.toLowerCase();
    const match = text.match(/i[5-9]-?(\d+)/);
    if (match) {
        const gen = parseInt(match[1].charAt(0));
        return gen >= 8;
    }
    return false;
}

// RAM 검증
function validateRAM(ramText) {
    if (!ramText) return false;
    const match = ramText.match(/(\d+)/);
    return match && parseInt(match[1]) >= 16;
}

// 키워드 체크
function checkKeyword(text, keywords) {
    if (!text) return false;
    const lowerText = text.toLowerCase();
    return keywords.some(keyword => lowerText.includes(keyword.toLowerCase()));
}

// 플랫폼 뱃지
function getPlatformBadge(source) {
    const badges = {
        '중고나라': '<span class="platform-badge joonggonara">중고나라</span>',
        '번개장터': '<span class="platform-badge bunjang">번개장터</span>',
        '당근마켓': '<span class="platform-badge daangn">당근마켓</span>',
        'eBay': '<span class="platform-badge ebay">eBay</span>'
    };
    return badges[source] || `<span class="platform-badge">${source}</span>`;
}

// 가격 포맷
function formatPrice(price) {
    if (!price) return '-';
    const num = parsePrice(price);
    if (num === 0) return price;
    return num.toLocaleString() + '원';
}

// 날짜 포맷
function formatDate(dateInput) {
    if (!dateInput) return '-';
    const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return '오늘';
    if (days === 1) return '어제';
    if (days < 7) return `${days}일 전`;

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 수집 시간 포맷 (연-월-일 시:분)
function formatTimestamp(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

// HTML 이스케이프
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 결과 없음 표시
function showNoResults() {
    resultsBody.innerHTML = '';
    noResults.style.display = 'block';
}
