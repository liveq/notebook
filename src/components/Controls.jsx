export default function Controls({ filter, setFilter, sortBy, setSortBy }) {
  return (
    <div className="controls-bar">
      <div className="filter-buttons">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          전체
        </button>
        <button
          className={`filter-btn ${filter === 'new' ? 'active' : ''}`}
          onClick={() => setFilter('new')}
        >
          신규만
        </button>
      </div>

      <div className="sort-buttons">
        <button
          className={`sort-btn ${sortBy === 'latest' ? 'active' : ''}`}
          onClick={() => setSortBy('latest')}
        >
          최신순
        </button>
        <button
          className={`sort-btn ${sortBy === 'price-low' ? 'active' : ''}`}
          onClick={() => setSortBy('price-low')}
        >
          가격 낮은순
        </button>
        <button
          className={`sort-btn ${sortBy === 'price-high' ? 'active' : ''}`}
          onClick={() => setSortBy('price-high')}
        >
          가격 높은순
        </button>
      </div>
    </div>
  )
}
