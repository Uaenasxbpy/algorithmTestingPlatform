import api from './index'

// 结果相关接口
export interface TestResult {
  id: number
  task_id: number
  metric_name: string
  value: number
  unit?: string
  test_round?: number
  created_at: string
}

export interface PerformanceMetrics {
  avg_keygen_time?: number
  avg_encaps_time?: number
  avg_decaps_time?: number
  avg_sign_time?: number
  avg_verify_time?: number
  success_rate: number
  public_key_size?: number
  private_key_size?: number
  signature_size?: number
  ciphertext_size?: number
}

export interface ResultSummary {
  [metricName: string]: {
    count: number
    avg: number
    min: number
    max: number
    median: number
    std_dev: number
  } | {
    task_info: {
      task_id: number
      task_name: string
      test_count: number
      algorithm_name: string
      category: string
    }
  }
}

export const resultApi = {
  // 获取任务结果
  getTaskResults: (taskId: number): Promise<TestResult[]> => {
    return api.get(`/results/task/${taskId}`)
  },

  // 获取任务结果摘要
  getTaskResultsSummary: (taskId: number): Promise<ResultSummary> => {
    return api.get(`/results/task/${taskId}/summary`)
  },

  // 获取任务性能指标
  getTaskPerformanceMetrics: (taskId: number): Promise<PerformanceMetrics> => {
    return api.get(`/results/task/${taskId}/metrics`)
  },

  // 比较算法性能
  compareAlgorithms: (params: {
    algorithm_ids: string
    metric_name?: string
  }): Promise<any> => {
    return api.get('/results/compare', { params })
  },

  // 获取算法最新结果
  getAlgorithmLatestResults: (params: {
    algorithm_id: number
    limit?: number
  }): Promise<TestResult[]> => {
    return api.get(`/results/algorithm/${params.algorithm_id}/latest`, {
      params: { limit: params.limit }
    })
  },

  // 获取算法性能历史
  getAlgorithmPerformanceHistory: (params: {
    algorithm_id: number
    metric_name: string
    days?: number
  }): Promise<any> => {
    return api.get(`/results/algorithm/${params.algorithm_id}/history`, {
      params: { metric_name: params.metric_name, days: params.days }
    })
  },
}