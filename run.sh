#!/bin/bash
# 중고 노트북 LTE 매물 검색 웹 서비스 실행 스크립트

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║       중고 노트북 LTE 매물 검색 웹 서비스               ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "가상환경을 생성합니다..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo "가상환경을 활성화합니다..."
source venv/bin/activate

# 의존성 설치
echo "의존성을 설치합니다..."
pip install -r requirements.txt

# 데이터 디렉토리 생성
mkdir -p data

# 웹 서버 실행
echo ""
echo "웹 서버를 시작합니다..."
echo ""
echo "접속 주소:"
echo "  - 로컬: http://localhost:5000"
echo "  - 네트워크: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "스마트폰에서 접속하려면 같은 WiFi에 연결 후"
echo "위의 네트워크 주소로 접속하세요."
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

python app.py
