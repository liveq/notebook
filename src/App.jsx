import { useState, useEffect } from 'react'
import Header from './components/Header'
import Stats from './components/Stats'
import Controls from './components/Controls'
import ResultCard from './components/ResultCard'
import './styles.css'

function App() {
  const [results, setResults] = useState([])
  const [filteredResults, setFilteredResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // 'all' or 'new'
  const [sortBy, setSortBy] = useState('latest') // 'latest', 'price-low', 'price-high'
  const [stats, setStats] = useState({
    total_count: 0,
    new_count: 0,
    price_range: {}
  })

  // 데이터 로드
  useEffect(() => {
    loadResults()
  }, [])

  // 필터/정렬 적용
  useEffect(() => {
    applyFilterAndSort()
  }, [results, filter, sortBy])

  const loadResults = async () => {
    try {
      // GitHub에 저장된 JSON 파일 로드
      const response = await fetch('/notebook/data/results.json')

      if (!response.ok) {
        throw new Error('데이터를 불러올 수 없습니다')
      }

      const data = await response.json()
      setResults(data.results || [])
      setStats(data.stats || {
        total_count: 0,
        new_count: 0,
        price_range: {}
      })
      setLoading(false)
    } catch (error) {
      console.error('데이터 로드 실패:', error)
      setLoading(false)
    }
  }

  const applyFilterAndSort = () => {
    let filtered = [...results]

    // 필터 적용
    if (filter === 'new') {
      filtered = filtered.filter(item => item.is_new)
    }

    // 정렬 적용
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'latest':
          return new Date(b.timestamp) - new Date(a.timestamp)
        case 'price-low':
          const priceA = a.specs?.price || Infinity
          const priceB = b.specs?.price || Infinity
          return priceA - priceB
        case 'price-high':
          const priceA2 = a.specs?.price || 0
          const priceB2 = b.specs?.price || 0
          return priceB2 - priceA2
        default:
          return 0
      }
    })

    setFilteredResults(filtered)
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>데이터 불러오는 중...</p>
      </div>
    )
  }

  return (
    <div className="app">
      <Header />

      <Stats stats={stats} />

      <Controls
        filter={filter}
        setFilter={setFilter}
        sortBy={sortBy}
        setSortBy={setSortBy}
      />

      <div className="results-container">
        {filteredResults.length === 0 ? (
          <div className="empty-state">
            <p>😢 조건에 맞는 매물이 없습니다</p>
            <p className="hint">검색은 매일 자동으로 실행됩니다</p>
          </div>
        ) : (
          filteredResults.map((item, index) => (
            <ResultCard key={index} item={item} />
          ))
        )}
      </div>

      <footer className="footer">
        <p>📱 모바일 & 데스크탑 반응형</p>
        <p className="note">검색은 매일 GitHub Actions로 자동 실행됩니다</p>
      </footer>
    </div>
  )
}

export default App
