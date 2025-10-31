// 데이터 저장소 (메모리 내)
let notebooks = [];

// DOM Elements
const form = document.getElementById('notebookForm');
const addBtn = document.getElementById('addBtn');
const resetBtn = document.getElementById('resetBtn');
const saveBtn = document.getElementById('saveBtn');
const loadFile = document.getElementById('loadFile');
const notebookList = document.getElementById('notebookList');

// 입력 필드들
const inputs = {
    manufacturer: document.getElementById('manufacturer'),
    model: document.getElementById('model'),
    cpu: document.getElementById('cpu'),
    ram: document.getElementById('ram'),
    lte: document.getElementById('lte'),
    rotate360: document.getElementById('rotate360'),
    touch: document.getElementById('touch'),
    thunderbolt: document.getElementById('thunderbolt'),
    price: document.getElementById('price'),
    condition: document.getElementById('condition'),
    memo: document.getElementById('memo')
};

// 조건 체크 UI 요소들
const checkElements = {
    cpu: document.getElementById('check-cpu'),
    ram: document.getElementById('check-ram'),
    lte: document.getElementById('check-lte'),
    rotate360: document.getElementById('check-rotate360'),
    touch: document.getElementById('check-touch'),
    thunderbolt: document.getElementById('check-thunderbolt')
};

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateCheckStatus();
});

// 이벤트 리스너 설정
function setupEventListeners() {
    // 입력 필드 변경 시 실시간 조건 체크
    Object.values(inputs).forEach(input => {
        input.addEventListener('input', updateCheckStatus);
    });

    // 버튼 이벤트
    addBtn.addEventListener('click', addNotebook);
    resetBtn.addEventListener('click', resetForm);
    saveBtn.addEventListener('click', saveToJSON);
    loadFile.addEventListener('change', loadFromJSON);
}

// 조건 검증 함수들
function validateCPU(cpuText) {
    if (!cpuText) return false;
    const text = cpuText.toLowerCase();

    // i5, i7, i9 포함 여부
    if (!text.includes('i5') && !text.includes('i7') && !text.includes('i9')) {
        return false;
    }

    // 세대 추출 (숫자 찾기)
    const match = text.match(/i[5-9]-?(\d+)/);
    if (match) {
        const generation = parseInt(match[1].charAt(0)); // 첫 번째 숫자가 세대
        return generation >= 8;
    }

    return false;
}

function validateRAM(ramText) {
    if (!ramText) return false;

    // 숫자 추출
    const match = ramText.match(/(\d+)/);
    if (match) {
        const ramSize = parseInt(match[1]);
        return ramSize >= 16;
    }

    return false;
}

function validateLTE(lteText) {
    if (!lteText) return false;
    const text = lteText.toLowerCase();
    return text.includes('lte') || text.includes('wwan') || text.includes('5g');
}

function validate360(rotateText) {
    if (!rotateText) return false;
    const text = rotateText.toLowerCase();
    return text.includes('360') || text.includes('2-in-1') || text.includes('컨버터블') || text.includes('convertible');
}

function validateTouch(touchText) {
    if (!touchText) return false;
    const text = touchText.toLowerCase();
    return text.includes('터치') || text.includes('touch');
}

function validateThunderbolt(tbText) {
    if (!tbText) return false;
    const text = tbText.toLowerCase();

    if (!text.includes('thunderbolt') && !text.includes('썬더볼트')) {
        return false;
    }

    // 버전 번호 추출
    const match = text.match(/(\d+)/);
    if (match) {
        const version = parseInt(match[1]);
        return version >= 3;
    }

    return false;
}

// 조건 검증 및 객체 생성
function validateConditions(data) {
    return {
        cpu: validateCPU(data.cpu),
        ram: validateRAM(data.ram),
        lte: validateLTE(data.lte),
        rotate360: validate360(data.rotate360),
        touch: validateTouch(data.touch),
        thunderbolt: validateThunderbolt(data.thunderbolt)
    };
}

// 실시간 조건 체크 업데이트
function updateCheckStatus() {
    const data = {
        cpu: inputs.cpu.value,
        ram: inputs.ram.value,
        lte: inputs.lte.value,
        rotate360: inputs.rotate360.value,
        touch: inputs.touch.value,
        thunderbolt: inputs.thunderbolt.value
    };

    const checks = validateConditions(data);

    // UI 업데이트
    Object.keys(checks).forEach(key => {
        const element = checkElements[key];
        const icon = element.querySelector('.check-icon');
        const value = data[key].trim();

        // 상태에 따라 클래스 변경
        element.classList.remove('pass', 'fail', 'unknown');

        if (!value) {
            element.classList.add('unknown');
            icon.textContent = '?';
        } else if (checks[key]) {
            element.classList.add('pass');
            icon.textContent = '✓';
        } else {
            element.classList.add('fail');
            icon.textContent = '✗';
        }
    });
}

// 매물 추가
function addNotebook() {
    const data = {
        id: Date.now(),
        manufacturer: inputs.manufacturer.value.trim(),
        model: inputs.model.value.trim(),
        cpu: inputs.cpu.value.trim(),
        ram: inputs.ram.value.trim(),
        lte: inputs.lte.value.trim(),
        rotate360: inputs.rotate360.value.trim(),
        touch: inputs.touch.value.trim(),
        thunderbolt: inputs.thunderbolt.value.trim(),
        price: inputs.price.value.trim(),
        condition: inputs.condition.value,
        memo: inputs.memo.value.trim()
    };

    // 필수 필드 검증
    if (!data.manufacturer || !data.model) {
        alert('제조사와 모델명은 필수 입력 항목입니다.');
        return;
    }

    // 조건 체크
    data.checks = validateConditions(data);

    // 배열에 추가
    notebooks.push(data);

    // 목록 렌더링
    renderList();

    // 폼 초기화
    resetForm();
}

// 목록 렌더링
function renderList() {
    if (notebooks.length === 0) {
        notebookList.innerHTML = `
            <tr class="empty-row">
                <td colspan="8">매물이 없습니다. 위 폼에서 매물을 추가하세요.</td>
            </tr>
        `;
        return;
    }

    notebookList.innerHTML = notebooks.map(item => {
        const checkCount = Object.values(item.checks).filter(v => v).length;
        const totalChecks = Object.keys(item.checks).length;

        let badgeClass = 'fail';
        let badgeText = `${checkCount}/${totalChecks}`;

        if (checkCount === totalChecks) {
            badgeClass = 'all-pass';
            badgeText = '모두 충족';
        } else if (checkCount > 0) {
            badgeClass = 'partial';
        }

        return `
            <tr>
                <td>${item.manufacturer}</td>
                <td>${item.model}</td>
                <td>${item.cpu}</td>
                <td>${item.ram}</td>
                <td>${item.price}</td>
                <td>${item.condition}</td>
                <td><span class="check-badge ${badgeClass}">${badgeText}</span></td>
                <td><button class="btn btn-delete" onclick="deleteNotebook(${item.id})">삭제</button></td>
            </tr>
        `;
    }).join('');
}

// 매물 삭제
function deleteNotebook(id) {
    if (confirm('정말 삭제하시겠습니까?')) {
        notebooks = notebooks.filter(item => item.id !== id);
        renderList();
    }
}

// 폼 초기화
function resetForm() {
    form.reset();
    updateCheckStatus();
}

// JSON 저장
function saveToJSON() {
    if (notebooks.length === 0) {
        alert('저장할 매물이 없습니다.');
        return;
    }

    const dataStr = JSON.stringify(notebooks, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });

    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `notebook-list-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();

    URL.revokeObjectURL(url);
}

// JSON 불러오기
function loadFromJSON(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);

            if (!Array.isArray(data)) {
                throw new Error('올바른 형식이 아닙니다.');
            }

            notebooks = data;
            renderList();
            alert(`${notebooks.length}개의 매물을 불러왔습니다.`);
        } catch (error) {
            alert('파일을 읽을 수 없습니다: ' + error.message);
        }
    };

    reader.readAsText(file);

    // 파일 input 초기화
    event.target.value = '';
}

// 전역 함수로 노출 (HTML onclick에서 사용)
window.deleteNotebook = deleteNotebook;
