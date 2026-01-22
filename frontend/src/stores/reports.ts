import { defineStore } from 'pinia'
import { reportApi, type Report } from '@/api/reports'

export const useReportStore = defineStore('reports', {
  state: () => ({
    reports: [] as Report[],
    taskReports: new Map<number, Report[]>(),
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getTaskReports: (state) => (taskId: number) => state.taskReports.get(taskId) || [],
    getReportById: (state) => (id: number) => state.reports.find(report => report.id === id),
  },

  actions: {
    async fetchAllReports(params?: { skip?: number; limit?: number }) {
      this.loading = true
      this.error = null

      try {
        const reports = await reportApi.getAllReports(params)
        this.reports = reports
        return reports
      } catch (error: any) {
        this.error = error.message || '获取报告列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTaskReports(taskId: number) {
      this.loading = true
      this.error = null

      try {
        const reports = await reportApi.getTaskReports(taskId)
        this.taskReports.set(taskId, reports)
        return reports
      } catch (error: any) {
        this.error = error.message || '获取任务报告失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async generateReport(taskId: number, reportType: 'pdf' | 'csv' = 'pdf') {
      this.loading = true
      this.error = null

      try {
        const report = await reportApi.generateReport(taskId, reportType)

        // 更新报告列表
        const existingReports = this.taskReports.get(taskId) || []
        this.taskReports.set(taskId, [...existingReports, report])

        // 更新全局报告列表
        this.reports.unshift(report)

        return report
      } catch (error: any) {
        this.error = error.message || '生成报告失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async batchGenerateReports(taskIds: number[], reportType: 'pdf' | 'csv' = 'pdf') {
      this.loading = true
      this.error = null

      try {
        const reports = await reportApi.batchGenerateReports(taskIds, reportType)

        // 更新报告列表
        this.reports.unshift(...reports)

        // 更新任务报告缓存
        reports.forEach(report => {
          const existingReports = this.taskReports.get(report.task_id) || []
          this.taskReports.set(report.task_id, [...existingReports, report])
        })

        return reports
      } catch (error: any) {
        this.error = error.message || '批量生成报告失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteReport(reportId: number) {
      this.loading = true
      this.error = null

      try {
        await reportApi.deleteReport(reportId)

        // 从全局列表中移除
        const globalIndex = this.reports.findIndex(report => report.id === reportId)
        if (globalIndex >= 0) {
          const report = this.reports[globalIndex]
          this.reports.splice(globalIndex, 1)

          // 从任务报告缓存中移除
          const taskReports = this.taskReports.get(report.task_id)
          if (taskReports) {
            const taskIndex = taskReports.findIndex(r => r.id === reportId)
            if (taskIndex >= 0) {
              taskReports.splice(taskIndex, 1)
            }
          }
        }
      } catch (error: any) {
        this.error = error.message || '删除报告失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    getDownloadUrl(reportId: number): string {
      return reportApi.downloadReport(reportId)
    },

    getPreviewUrl(reportId: number): string {
      return reportApi.previewReport(reportId)
    },

    clearError() {
      this.error = null
    },

    clearTaskReports(taskId: number) {
      this.taskReports.delete(taskId)
    },
  },
})