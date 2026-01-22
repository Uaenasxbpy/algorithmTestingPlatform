import api from './index'

// 报告相关接口
export interface Report {
  id: number
  task_id: number
  report_name: string
  file_path: string
  file_type: string
  file_size?: number
  created_at: string
}

export const reportApi = {
  // 获取任务报告
  getTaskReports: (taskId: number): Promise<Report[]> => {
    return api.get(`/reports/task/${taskId}`)
  },

  // 生成报告
  generateReport: (taskId: number, reportType: 'pdf' | 'csv' = 'pdf'): Promise<Report> => {
    return api.post(`/reports/task/${taskId}/generate`, null, {
      params: { report_type: reportType }
    })
  },

  // 下载报告
  downloadReport: (reportId: number): string => {
    return `${api.defaults.baseURL}/reports/${reportId}/download`
  },

  // 预览报告
  previewReport: (reportId: number): string => {
    return `${api.defaults.baseURL}/reports/${reportId}/preview`
  },

  // 删除报告
  deleteReport: (reportId: number): Promise<{ message: string; success: boolean }> => {
    return api.delete(`/reports/${reportId}`)
  },

  // 批量生成报告
  batchGenerateReports: (taskIds: number[], reportType: 'pdf' | 'csv' = 'pdf'): Promise<Report[]> => {
    return api.post('/reports/batch-generate', taskIds, {
      params: { report_type: reportType }
    })
  },

  // 获取所有报告
  getAllReports: (params?: {
    skip?: number
    limit?: number
  }): Promise<Report[]> => {
    return api.get('/reports', { params })
  },
}