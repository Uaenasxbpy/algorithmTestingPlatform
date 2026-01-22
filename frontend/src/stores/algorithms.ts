import { defineStore } from 'pinia'
import { algorithmApi, type Algorithm, type AlgorithmCreate, type AlgorithmUpdate } from '@/api/algorithms'

export const useAlgorithmStore = defineStore('algorithms', {
  state: () => ({
    algorithms: [] as Algorithm[],
    loading: false,
    error: null as string | null,
  }),

  getters: {
    kemAlgorithms: (state) => state.algorithms.filter(alg => alg.category === 'KEM'),
    signatureAlgorithms: (state) => state.algorithms.filter(alg => alg.category === 'SIGNATURE'),
    activeAlgorithms: (state) => state.algorithms.filter(alg => alg.is_active),
    getAlgorithmById: (state) => (id: number) => state.algorithms.find(alg => alg.id === id),
  },

  actions: {
    async fetchAlgorithms(params?: {
      skip?: number
      limit?: number
      category?: string
      is_active?: boolean
    }) {
      this.loading = true
      this.error = null
      
      try {
        const algorithms = await algorithmApi.getAlgorithms(params)
        this.algorithms = algorithms
      } catch (error: any) {
        this.error = error.message || '获取算法列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchAlgorithm(id: number) {
      this.loading = true
      this.error = null
      
      try {
        const algorithm = await algorithmApi.getAlgorithm(id)
        const index = this.algorithms.findIndex(alg => alg.id === id)
        if (index >= 0) {
          this.algorithms[index] = algorithm
        } else {
          this.algorithms.push(algorithm)
        }
        return algorithm
      } catch (error: any) {
        this.error = error.message || '获取算法详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createAlgorithm(data: AlgorithmCreate) {
      this.loading = true
      this.error = null
      
      try {
        const algorithm = await algorithmApi.createAlgorithm(data)
        this.algorithms.push(algorithm)
        return algorithm
      } catch (error: any) {
        this.error = error.message || '创建算法失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateAlgorithm(id: number, data: AlgorithmUpdate) {
      this.loading = true
      this.error = null
      
      try {
        const algorithm = await algorithmApi.updateAlgorithm(id, data)
        const index = this.algorithms.findIndex(alg => alg.id === id)
        if (index >= 0) {
          this.algorithms[index] = algorithm
        }
        return algorithm
      } catch (error: any) {
        this.error = error.message || '更新算法失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteAlgorithm(id: number) {
      this.loading = true
      this.error = null
      
      try {
        await algorithmApi.deleteAlgorithm(id)
        const index = this.algorithms.findIndex(alg => alg.id === id)
        if (index >= 0) {
          this.algorithms.splice(index, 1)
        }
      } catch (error: any) {
        this.error = error.message || '删除算法失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async testAlgorithm(id: number) {
      this.loading = true
      this.error = null
      
      try {
        const result = await algorithmApi.testAlgorithm(id)
        return result
      } catch (error: any) {
        this.error = error.message || '测试算法失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    clearError() {
      this.error = null
    },
  },
})