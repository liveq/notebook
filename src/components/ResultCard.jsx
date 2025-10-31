export default function ResultCard({ item }) {
  const formatPrice = (price) => {
    if (!price) return '가격 문의'
    if (price >= 10000) {
      return `${Math.floor(price / 10000)}만원`
    }
    return `${price.toLocaleString()}원`
  }

  return (
    <div className={`result-card ${item.is_new ? 'new' : ''}`}>
      <div className="card-header">
        <div className="card-title">{item.title}</div>
        <div className="card-badges">
          {item.is_new && <span className="badge badge-new">NEW</span>}
          <span className="badge badge-source">{item.source}</span>
        </div>
      </div>

      <div className="card-price">{formatPrice(item.specs?.price)}</div>

      <div className="card-specs">
        <div className="spec-item">💻 {item.specs?.cpu || '정보 없음'}</div>
        <div className="spec-item">
          🧠 {item.specs?.ram ? `${item.specs.ram}GB` : '정보 없음'}
        </div>
      </div>

      {item.matched_keywords && item.matched_keywords.length > 0 && (
        <div className="card-keywords">
          {item.matched_keywords.map((keyword, idx) => (
            <span key={idx} className="keyword">
              {keyword}
            </span>
          ))}
        </div>
      )}

      <div className="card-footer">
        <div className="card-location">📍 {item.location || '위치 정보 없음'}</div>
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-view"
        >
          상세보기
        </a>
      </div>
    </div>
  )
}
