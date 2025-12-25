/**
 * API client for communicating with CodeSentinel backend
 */

import axios, { AxiosInstance } from 'axios'
import { ScanRequest, ScanResult, ScanProgress, ProjectHistoryItem } from '@types'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

class CodeSentinelAPI {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      timeout: 300000, // 5 minutes for long scans
    })
  }

  /**
   * Health check
   */
  async healthCheck() {
    return this.client.get('/health')
  }

  /**
   * Get API configuration
   */
  async getConfig() {
    return this.client.get('/config')
  }

  /**
   * Start a new scan
   */
  async startScan(request: ScanRequest): Promise<ScanResult> {
    const response = await this.client.post('/scans', request)
    return response.data
  }

  /**
   * Get scan results by ID
   */
  async getScanResults(scanId: string): Promise<ScanResult> {
    const response = await this.client.get(`/scans/${scanId}`)
    return response.data
  }

  /**
   * Subscribe to real-time progress updates via WebSocket
   */
  subscribeToProgress(
    scanId: string,
    onProgress: (progress: ScanProgress) => void,
    onError: (error: Error) => void
  ): () => void {
    const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/api/scans/${scanId}/progress`
    const ws = new WebSocket(wsUrl)

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onProgress(data)
      } catch (error) {
        onError(new Error('Failed to parse progress update'))
      }
    }

    ws.onerror = (event) => {
      onError(new Error('WebSocket error'))
    }

    // Return cleanup function
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }

  /**
   * Cancel a scan
   */
  async cancelScan(scanId: string) {
    return this.client.delete(`/scans/${scanId}`)
  }

  /**
   * Get finding details
   */
  async getFinding(findingId: string) {
    return this.client.get(`/findings/${findingId}`)
  }

  /**
   * Update finding status
   */
  async updateFinding(findingId: string, updateData: any) {
    return this.client.patch(`/findings/${findingId}`, updateData)
  }

  /**
   * Add notes to a finding
   */
  async addFindingNotes(findingId: string, notes: string) {
    return this.client.post(`/findings/${findingId}/notes`, { notes })
  }

  /**
   * Get project history
   */
  async getProjects(): Promise<ProjectHistoryItem[]> {
    const response = await this.client.get('/projects')
    return response.data
  }

  /**
   * Get scans for a specific project
   */
  async getProjectScans(projectPath: string) {
    return this.client.get(`/projects/${encodeURIComponent(projectPath)}/scans`)
  }

  /**
   * Delete project from history
   */
  async deleteProject(projectPath: string) {
    return this.client.delete(`/projects/${encodeURIComponent(projectPath)}`)
  }
}

export const api = new CodeSentinelAPI()
