/**
 * Core type definitions for CodeSentinel GUI
 */

export interface ScanRequest {
  target_path: string
  enable_ai: boolean
  llm_provider: string
  include_patterns: string[]
  exclude_patterns: string[]
}

export interface Finding {
  id: string
  rule_id: string
  rule_name: string
  file_path: string
  line?: number
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  confidence: number
  excerpt?: string
  category: string
  tags: string[]
  ai_explanation?: string
  remediation?: string
  cwe_id?: string
  risk_score?: number
  references: string[]
  is_resolved: boolean
  user_notes: string
}

export interface ScanSummary {
  scan_id: string
  total_files: number
  files_with_issues: number
  total_findings: number
  severity_breakdown: Record<string, number>
  scan_duration_seconds: number
  ai_enabled: boolean
  llm_provider?: string
}

export interface ScanResult {
  scan_id: string
  summary: ScanSummary
  findings: Finding[]
  recommendations?: {
    immediate_actions: string[]
    prevention: string[]
    priority_fixes: string[]
    technical_debt: string[]
  }
}

export interface ScanProgress {
  scan_id: string
  status: 'queued' | 'in_progress' | 'completed' | 'failed' | 'cancelled'
  current_file?: string
  files_processed: number
  total_files: number
  findings_count: number
  estimated_time_remaining?: number
  progress_percentage: number
  current_operation?: string
  timestamp: string
}

export interface ProjectHistoryItem {
  project_path: string
  last_scan_date: string
  finding_count: number
  severity_breakdown: Record<string, number>
}
