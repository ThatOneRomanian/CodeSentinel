import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@services/api'
import { ScanRequest } from '@types'
import './Dashboard.css'

function Dashboard() {
  const navigate = useNavigate()
  const [targetPath, setTargetPath] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [enableAI, setEnableAI] = useState(false)

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const request: ScanRequest = {
        target_path: targetPath,
        enable_ai: enableAI,
        llm_provider: 'deepseek',
        include_patterns: ['*.py', '*.js', '*.json', '*.yaml', '*.yml', '*.env'],
        exclude_patterns: ['.git', 'node_modules', '__pycache__', '.pytest_cache'],
      }

      const result = await api.startScan(request)
      navigate(`/results/${result.scan_id}`)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to start scan'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>CodeSentinel</h1>
          <p>AI-Powered Security Scanner</p>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="scan-form-container">
          <form onSubmit={handleScan} className="scan-form">
            <h2>Start a Security Scan</h2>

            <div className="form-group">
              <label htmlFor="targetPath">Project Directory</label>
              <input
                id="targetPath"
                type="text"
                placeholder="/path/to/your/project"
                value={targetPath}
                onChange={(e) => setTargetPath(e.target.value)}
                required
                disabled={loading}
                className="form-input"
              />
              <small>Enter the path to the directory you want to scan</small>
            </div>

            <div className="form-group checkbox">
              <label>
                <input
                  type="checkbox"
                  checked={enableAI}
                  onChange={(e) => setEnableAI(e.target.checked)}
                  disabled={loading}
                />
                <span>Enable AI-powered explanations (requires DEEPSEEK_API_KEY)</span>
              </label>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              disabled={loading || !targetPath}
              className="btn-primary"
            >
              {loading ? 'Scanning...' : 'Start Scan'}
            </button>
          </form>

          <div className="info-panel">
            <h3>Features</h3>
            <ul>
              <li>🔐 Secret Detection - API keys, tokens, passwords</li>
              <li>⚙️ Configuration Scanning - Insecure settings</li>
              <li>🐳 Docker Security - Container best practices</li>
              <li>🤖 GitHub Actions - CI/CD security</li>
              <li>🌳 Terraform Security - IaC vulnerabilities</li>
              <li>📦 Supply Chain - Dependency security</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
