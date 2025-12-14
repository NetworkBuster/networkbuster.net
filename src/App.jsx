import { useState } from 'react'
import './App.css'
import TeamMembers from './TeamMembers'
import Overlay from './Overlay'
import Dashboard from './Dashboard'

function App() {
  const [count, setCount] = useState(0)
  const [currentPage, setCurrentPage] = useState('overlay')

  const handleNavigation = (e, page) => {
    e.preventDefault()
    setCurrentPage(page)
    window.scrollTo(0, 0)
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🚀 NetworkBuster - Real-Time Overlay & Dashboard</h1>
        <p>Vite React Frontend on Port 5173</p>
      </header>

      <nav className="app-nav">
        <ul>
          <li><a href="/overlay" onClick={(e) => handleNavigation(e, 'overlay')}>Overlay</a></li>
          <li><a href="/dashboard" onClick={(e) => handleNavigation(e, 'dashboard')}>Dashboard</a></li>
          <li><a href="/team" onClick={(e) => handleNavigation(e, 'team')}>Team</a></li>
          <li><a href="http://localhost:3001/home" target="_blank">Backend Home</a></li>
        </ul>
      </nav>

      <main className="app-main">
        {currentPage === 'overlay' && <Overlay />}
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'team' && <TeamMembers />}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 NetworkBuster Development Platform</p>
      </footer>
    </div>
  )
}

export default App
