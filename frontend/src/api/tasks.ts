import api from './index'
import type { Algorithm } from './algorithms'

// 任务相关接口
export interface TestTask {
  id: number
  algorithm_id: number
  task_name: string
  parameters?: Record<string, any>
  test_count: number
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  error_message?: string
  started_at?: string
  finished_at?: string
  created_at: string
  algorithm: Algorithm
}

export interface TestTaskCreate {
  algorithm_id: number
  task_name: string
  parameters?: Record<string, any>
  test_count: number
}

export interface TestTaskUpdate {
  task_name?: string
  parameters?: Record<string, any>
  test_count?: number
  status?: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  error_message?: string
}

export interface TestExecutionRequest {
  algorithm_id: number
  test_name: string
  test_count: number
  parameters?: Record<string, any>
}

export interface TaskStatus {
  task_id: number
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  progress: number
  started_at?: string
  finished_at?: string
  error_message?: string
}

export const taskApi = {
  // 获取任务列表
  getTasks: (params?: {
    skip?: number
    limit?: number
    algorithm_id?: number
    status_filter?: string
  }): Promise<TestTask[]> => {
    return api.get('/tasks', { params })
  },

  // 根据ID获取任务
  getTask: (id: number): Promise<TestTask> => {
    return api.get(`/tasks/${id}`)
  },

  // 创建任务
  createTask: (data: TestTaskCreate): Promise<TestTask> => {
    return api.post('/tasks', data)
  },

  // 执行测试
  executeTest: (data: TestExecutionRequest): Promise<{ message: string; success: boolean }> => {
    return api.post('/tasks/execute', data)
  },

  // 更新任务
  updateTask: (id: number, data: TestTaskUpdate): Promise<TestTask> => {
    return api.put(`/tasks/${id}`, data)
  },

  // 删除任务
  deleteTask: (id: number): Promise<{ message: string; success: boolean }> => {
    return api.delete(`/tasks/${id}`)
  },

  // 停止任务
  stopTask: (id: number): Promise<{ message: string; success: boolean }> => {
    return api.post(`/tasks/${id}/stop`)
  },

  // 获取任务状态
  getTaskStatus: (id: number): Promise<TaskStatus> => {
    return api.get(`/tasks/${id}/status`)
  },
  
  // 手动运行任务
  runTask: (id: number): Promise<{ message: string; success: boolean }> => {
    return api.post(`/tasks/${id}/run`)
  },
}