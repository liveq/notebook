export default function Stats({ stats }) {
  const formatPriceRange = () => {
    const { min, max } = stats.price_range || {}
    if (!min || !max) return '-'
    return `${Math.floor(min / 10000)}~${Math.floor(max / 10000)}만원`
  }

  return (
    <div className="stats-section">
      <div className="stat-card">
        <div className="stat-value">{stats.total_count || 0}</div>
        <div className="stat-label">총 매물</div>
      </div>
      <div className="stat-card">
        <div className="stat-value new">{stats.new_count || 0}</div>
        <div className="stat-label">신규 매물</div>
      </div>
      <div className="stat-card">
        <div className="stat-value">{formatPriceRange()}</div>
        <div className="stat-label">가격대</div>
      </div>
    </div>
  )
}
