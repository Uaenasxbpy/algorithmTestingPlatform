import { defineStore } from 'pinia'
import { resultApi, type TestResult, type PerformanceMetrics, type ResultSummary } from '@/api/results'

export const useResultStore = defineStore('results', {
  state: () => ({
    taskResults: new Map<number, TestResult[]>(),
    taskSummaries: new Map<number, ResultSummary>(),
    taskMetrics: new Map<number, PerformanceMetrics>(),
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getTaskResults: (state) => (taskId: number) => state.taskResults.get(taskId) || [],
    getTaskSummary: (state) => (taskId: number) => state.taskSummaries.get(taskId),
    getTaskMetrics: (state) => (taskId: number) => state.taskMetrics.get(taskId),
  },

  actions: {
    async fetchTaskResults(taskId: number) {
      this.loading = true
      this.error = null
      
      try {
        const results = await resultApi.getTaskResults(taskId)
        this.taskResults.set(taskId, results)
        return results
      } catch (error: any) {
        this.error = error.message || '获取任务结果失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTaskResultsSummary(taskId: number) {
      this.loading = true
      this.error = null
      
      try {
        const summary = await resultApi.getTaskResultsSummary(taskId)
        this.taskSummaries.set(taskId, summary)
        return summary
      } catch (error: any) {
        this.error = error.message || '获取任务结果摘要失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTaskPerformanceMetrics(taskId: number) {
      this.loading = true
      this.error = null
      
      try {
        const metrics = await resultApi.getTaskPerformanceMetrics(taskId)
        this.taskMetrics.set(taskId, metrics)
        return metrics
      } catch (error: any) {
        this.error = error.message || '获取性能指标失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async compareAlgorithms(algorithmIds: number[], metricName?: string) {
      this.loading = true
      this.error = null
      
      try {
        const comparison = await resultApi.compareAlgorithms({
          algorithm_ids: algorithmIds.join(','),
          metric_name: metricName
        })
        return comparison
      } catch (error: any) {
        this.error = error.message || '算法对比失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchAlgorithmLatestResults(algorithmId: number, limit: number = 10) {
      this.loading = true
      this.error = null
      
      try {
        const results = await resultApi.getAlgorithmLatestResults({
          algorithm_id: algorithmId,
          limit
        })
        return results
      } catch (error: any) {
        this.error = error.message || '获取算法最新结果失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchAlgorithmPerformanceHistory(algorithmId: number, metricName: string, days: number = 30) {
      this.loading = true
      this.error = null
      
      try {
        const history = await resultApi.getAlgorithmPerformanceHistory({
          algorithm_id: algorithmId,
          metric_name: metricName,
          days
        })
        return history
      } catch (error: any) {
        this.error = error.message || '获取性能历史失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    clearError() {
      this.error = null
    },

    clearTaskData(taskId: number) {
      this.taskResults.delete(taskId)
      this.taskSummaries.delete(taskId)
      this.taskMetrics.delete(taskId)
    },
  },
})