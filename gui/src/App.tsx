import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from '@pages/Dashboard'
import ScanResults from '@pages/ScanResults'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/results/:scanId" element={<ScanResults />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
