import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🚀 NetworkBuster - Unified Dev Environment</h1>
        <p>Express Backend + Vite React Frontend</p>
      </header>

      <nav className="app-nav">
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/ai-world">AI World</a></li>
          <li><a href="/control-panel">Control Panel</a></li>
        </ul>
      </nav>

      <main className="app-main">
        <section className="welcome-section">
          <h2>Welcome to NetworkBuster</h2>
          <p>This is a React frontend powered by Vite, integrated with an Express.js backend.</p>
          
          <div className="button-group">
            <button onClick={() => setCount(count + 1)} className="primary-btn">
              Counter: {count}
            </button>
            <button onClick={() => setCount(0)} className="secondary-btn">
              Reset
            </button>
          </div>
        </section>

        <section className="features-section">
          <h3>Features</h3>
          <ul className="features-list">
            <li>⚡ Vite fast development server with HMR</li>
            <li>🔗 API proxy to Express backend</li>
            <li>🎨 React with modern tooling</li>
            <li>📊 Unified full-stack development</li>
            <li>🚀 Production-ready build system</li>
          </ul>
        </section>

        <section className="servers-section">
          <h3>Running Servers</h3>
          <ul className="servers-list">
            <li>Frontend: <strong>http://localhost:5173</strong></li>
            <li>Backend: <strong>http://localhost:3000</strong></li>
          </ul>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 NetworkBuster Development Platform</p>
      </footer>
    </div>
  )
}

export default App
