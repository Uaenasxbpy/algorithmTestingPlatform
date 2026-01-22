import api from './index'

// 算法相关接口
export interface Algorithm {
  id: number
  name: string
  category: 'KEM' | 'SIGNATURE'
  source: string
  version?: string
  description?: string
  library_name?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface AlgorithmCreate {
  name: string
  category: 'KEM' | 'SIGNATURE'
  source: string
  version?: string
  description?: string
  library_name?: string
}

export interface AlgorithmUpdate {
  name?: string
  category?: 'KEM' | 'SIGNATURE'
  source?: string
  version?: string
  description?: string
  library_name?: string
  is_active?: boolean
}

export const algorithmApi = {
  // 获取算法列表
  getAlgorithms: (params?: {
    skip?: number
    limit?: number
    category?: string
    is_active?: boolean
  }): Promise<Algorithm[]> => {
    return api.get('/algorithms', { params })
  },

  // 根据ID获取算法
  getAlgorithm: (id: number): Promise<Algorithm> => {
    return api.get(`/algorithms/${id}`)
  },

  // 创建算法
  createAlgorithm: (data: AlgorithmCreate): Promise<Algorithm> => {
    return api.post('/algorithms', data)
  },

  // 更新算法
  updateAlgorithm: (id: number, data: AlgorithmUpdate): Promise<Algorithm> => {
    return api.put(`/algorithms/${id}`, data)
  },

  // 删除算法
  deleteAlgorithm: (id: number): Promise<{ message: string; success: boolean }> => {
    return api.delete(`/algorithms/${id}`)
  },

  // 测试算法可用性
  testAlgorithm: (id: number): Promise<{ message: string; success: boolean }> => {
    return api.get(`/algorithms/${id}/test`)
  },
}