import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@services/api'
import { ScanResult, Finding } from '@types'
import SeverityBadge from '@components/SeverityBadge'
import './ScanResults.css'

function ScanResults() {
  const { scanId } = useParams<{ scanId: string }>()
  const navigate = useNavigate()
  const [result, setResult] = useState<ScanResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null)
  const [severityFilter, setSeverityFilter] = useState<string | null>(null)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        if (!scanId) return
        const data = await api.getScanResults(scanId)
        setResult(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results')
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [scanId])

  if (loading) {
    return (
      <div className="scan-results">
        <div className="loading">Loading scan results...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="scan-results">
        <div className="error">{error}</div>
        <button onClick={() => navigate('/')} className="btn-secondary">
          Back to Dashboard
        </button>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="scan-results">
        <div className="error">No results found</div>
      </div>
    )
  }

  const filteredFindings = severityFilter
    ? result.findings.filter((f) => f.severity === severityFilter)
    : result.findings

  return (
    <div className="scan-results">
      <header className="results-header">
        <button onClick={() => navigate('/')} className="btn-back">
          ← Back
        </button>
        <h1>Scan Results</h1>
      </header>

      <div className="results-container">
        <div className="summary-panel">
          <h2>Summary</h2>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="label">Total Findings</span>
              <span className="value">{result.summary.total_findings}</span>
            </div>
            <div className="summary-item">
              <span className="label">Files Scanned</span>
              <span className="value">{result.summary.total_files}</span>
            </div>
            <div className="summary-item">
              <span className="label">Files with Issues</span>
              <span className="value">{result.summary.files_with_issues}</span>
            </div>
            <div className="summary-item">
              <span className="label">Scan Duration</span>
              <span className="value">{result.summary.scan_duration_seconds.toFixed(2)}s</span>
            </div>
          </div>

          <div className="severity-breakdown">
            <h3>Severity Breakdown</h3>
            {Object.entries(result.summary.severity_breakdown).map(([severity, count]) => (
              <div key={severity} className="severity-row">
                <button
                  onClick={() => setSeverityFilter(severityFilter === severity ? null : severity)}
                  className={`severity-filter ${severityFilter === severity ? 'active' : ''}`}
                >
                  <SeverityBadge severity={severity as any} />
                  <span>{count}</span>
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="findings-panel">
          <h2>Findings ({filteredFindings.length})</h2>
          <div className="findings-list">
            {filteredFindings.map((finding) => (
              <div
                key={finding.id}
                className={`finding-item ${selectedFinding?.id === finding.id ? 'selected' : ''}`}
                onClick={() => setSelectedFinding(finding)}
              >
                <div className="finding-header">
                  <SeverityBadge severity={finding.severity} />
                  <span className="rule-name">{finding.rule_name}</span>
                </div>
                <div className="finding-file">{finding.file_path}</div>
                {finding.line && <div className="finding-line">Line {finding.line}</div>}
              </div>
            ))}
          </div>
        </div>

        {selectedFinding && (
          <div className="detail-panel">
            <h2>Details</h2>
            <div className="detail-content">
              <div className="detail-row">
                <label>Rule:</label>
                <span>{selectedFinding.rule_name}</span>
              </div>
              <div className="detail-row">
                <label>File:</label>
                <span>{selectedFinding.file_path}</span>
              </div>
              {selectedFinding.line && (
                <div className="detail-row">
                  <label>Line:</label>
                  <span>{selectedFinding.line}</span>
                </div>
              )}
              <div className="detail-row">
                <label>Severity:</label>
                <SeverityBadge severity={selectedFinding.severity} />
              </div>
              <div className="detail-row">
                <label>Confidence:</label>
                <span>{(selectedFinding.confidence * 100).toFixed(0)}%</span>
              </div>

              {selectedFinding.excerpt && (
                <div className="detail-row">
                  <label>Code:</label>
                  <code className="excerpt">{selectedFinding.excerpt}</code>
                </div>
              )}

              {selectedFinding.ai_explanation && (
                <div className="detail-row">
                  <label>AI Explanation:</label>
                  <p>{selectedFinding.ai_explanation}</p>
                </div>
              )}

              {selectedFinding.remediation && (
                <div className="detail-row">
                  <label>Remediation:</label>
                  <p>{selectedFinding.remediation}</p>
                </div>
              )}

              {selectedFinding.references.length > 0 && (
                <div className="detail-row">
                  <label>References:</label>
                  <ul className="references">
                    {selectedFinding.references.map((ref) => (
                      <li key={ref}>
                        <a href={ref} target="_blank" rel="noopener noreferrer">
                          {ref}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ScanResults
