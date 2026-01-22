import { defineStore } from 'pinia'
import { taskApi, type TestTask, type TestTaskCreate, type TestExecutionRequest, type TaskStatus } from '@/api/tasks'

export const useTaskStore = defineStore('tasks', {
  state: () => ({
    tasks: [] as TestTask[],
    currentTask: null as TestTask | null,
    taskStatuses: new Map<number, TaskStatus>(),
    loading: false,
    error: null as string | null,
  }),

  getters: {
    pendingTasks: (state) => state.tasks.filter(task => task.status === 'PENDING'),
    runningTasks: (state) => state.tasks.filter(task => task.status === 'RUNNING'),
    completedTasks: (state) => state.tasks.filter(task => task.status === 'COMPLETED'),
    failedTasks: (state) => state.tasks.filter(task => task.status === 'FAILED'),
    getTaskById: (state) => (id: number) => state.tasks.find(task => task.id === id),
    getTaskStatus: (state) => (id: number) => state.taskStatuses.get(id),
  },

  actions: {
    async fetchTasks(params?: {
      skip?: number
      limit?: number
      algorithm_id?: number
      status_filter?: string
    }) {
      this.loading = true
      this.error = null
      
      try {
        const tasks = await taskApi.getTasks(params)
        this.tasks = tasks
      } catch (error: any) {
        this.error = error.message || '获取任务列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTask(id: number) {
      this.loading = true
      this.error = null
      
      try {
        const task = await taskApi.getTask(id)
        this.currentTask = task
        
        const index = this.tasks.findIndex(t => t.id === id)
        if (index >= 0) {
          this.tasks[index] = task
        } else {
          this.tasks.push(task)
        }
        
        return task
      } catch (error: any) {
        this.error = error.message || '获取任务详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createTask(data: TestTaskCreate) {
      this.loading = true
      this.error = null
      
      try {
        const task = await taskApi.createTask(data)
        this.tasks.unshift(task)
        return task
      } catch (error: any) {
        this.error = error.message || '创建任务失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async executeTest(data: TestExecutionRequest) {
      this.loading = true
      this.error = null
      
      try {
        const result = await taskApi.executeTest(data)
        // 刷新任务列表
        await this.fetchTasks()
        return result
      } catch (error: any) {
        this.error = error.message || '执行测试失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteTask(id: number) {
      this.loading = true
      this.error = null
      
      try {
        await taskApi.deleteTask(id)
        const index = this.tasks.findIndex(task => task.id === id)
        if (index >= 0) {
          this.tasks.splice(index, 1)
        }
        
        // 清除状态缓存
        this.taskStatuses.delete(id)
        
        if (this.currentTask?.id === id) {
          this.currentTask = null
        }
      } catch (error: any) {
        this.error = error.message || '删除任务失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async stopTask(id: number) {
      this.loading = true
      this.error = null
      
      try {
        const result = await taskApi.stopTask(id)
        // 更新任务状态
        await this.fetchTask(id)
        return result
      } catch (error: any) {
        this.error = error.message || '停止任务失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTaskStatus(id: number) {
      try {
        const status = await taskApi.getTaskStatus(id)
        this.taskStatuses.set(id, status)
        
        // 更新任务列表中的状态
        const taskIndex = this.tasks.findIndex(task => task.id === id)
        if (taskIndex >= 0) {
          this.tasks[taskIndex].status = status.status
        }
        
        // 更新当前任务状态
        if (this.currentTask?.id === id) {
          this.currentTask.status = status.status
        }
        
        return status
      } catch (error: any) {
        console.error('获取任务状态失败:', error)
        throw error
      }
    },

    // 轮询获取任务状态
    startPollingTaskStatus(id: number, interval: number = 2000) {
      const poll = async () => {
        try {
          const status = await this.fetchTaskStatus(id)
          
          // 如果任务已完成或失败，停止轮询
          if (status.status === 'COMPLETED' || status.status === 'FAILED') {
            return
          }
          
          // 继续轮询
          setTimeout(poll, interval)
        } catch (error) {
          console.error('轮询任务状态错误:', error)
        }
      }
      
      poll()
    },

    clearError() {
      this.error = null
    },

    setCurrentTask(task: TestTask | null) {
      this.currentTask = task
    },
  },
})