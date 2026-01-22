<template>
  <div class="results-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>结果分析</h2>
      <div class="header-actions">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 筛选器 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="选择任务">
          <el-select v-model="filters.taskId" placeholder="请选择任务" style="width: 250px">
            <el-option 
              v-for="task in completedTasks"
              :key="task.id"
              :label="`${task.task_name} (${task.algorithm.name})`"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadTaskResults" :disabled="!filters.taskId">
            分析结果
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果展示 -->
    <div v-if="selectedTask" class="results-content">
      <!-- 任务基本信息 -->
      <el-card class="task-info-card">
        <template #header>
          <div class="card-header">
            <el-icon><info-filled /></el-icon>
            <span>任务信息</span>
          </div>
        </template>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="任务名称">
                {{ selectedTask.task_name }}
              </el-descriptions-item>
              <el-descriptions-item label="算法名称">
                <el-tag :type="selectedTask.algorithm.category === 'KEM' ? 'primary' : 'success'">
                  {{ selectedTask.algorithm.name }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="测试次数">
                {{ selectedTask.test_count }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="开始时间">
                {{ formatDate(selectedTask.started_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="完成时间">
                {{ formatDate(selectedTask.finished_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="执行时长">
                {{ getExecutionDuration() }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
      </el-card>

      <!-- 性能指标概览 -->
      <el-card v-if="performanceMetrics" class="metrics-card">
        <template #header>
          <div class="card-header">
            <el-icon><PieChart /></el-icon>
            <span>性能指标概览</span>
          </div>
        </template>
        
        <el-row :gutter="16">
          <!-- KEM算法指标 -->
          <template v-if="selectedTask.algorithm.category === 'KEM'">
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-item">
                <div class="metric-value">{{ formatMetricValue(performanceMetrics.avg_keygen_time) }} ms</div>
                <div class="metric-label">平均密钥生成时间</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-item">
                <div class="metric-value">{{ formatMetricValue(performanceMetrics.avg_encaps_time) }} ms</div>
                <div class="metric-label">平均封装时间</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-item">
                <div class="metric-value">{{ formatMetricValue(performanceMetrics.avg_decaps_time) }} ms</div>
                <div class="metric-label">平均解封装时间</div>
              </div>
            </el-col>
          </template>
          
          <!-- 签名算法指标 -->
          <template v-else>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-item">
                <div class="metric-value">{{ formatMetricValue(performanceMetrics.avg_keygen_time) }} ms</div>
                <div class="metric-label">平均密钥生成时间</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-item">
                <div class="metric-value">{{ formatMetricValue(performanceMetrics.avg_sign_time) }} ms</div>
                <div class="metric-label">平均签名时间</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-item">
                <div class="metric-value">{{ formatMetricValue(performanceMetrics.avg_verify_time) }} ms</div>
                <div class="metric-label">平均验证时间</div>
              </div>
            </el-col>
          </template>
          
          <!-- 通用指标 -->
          <el-col :xs="24" :sm="12" :lg="6">
            <div class="metric-item success-rate">
              <div class="metric-value">{{ formatMetricValue(performanceMetrics.success_rate) }}%</div>
              <div class="metric-label">成功率</div>
            </div>
          </el-col>
        </el-row>
        
        <!-- 密钥大小信息 -->
        <el-divider />
        <el-row :gutter="16">
          <el-col :xs="24" :sm="8">
            <div class="size-info">
              <div class="size-label">公钥大小</div>
              <div class="size-value">{{ formatBytes(performanceMetrics.public_key_size) }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="size-info">
              <div class="size-label">私钥大小</div>
              <div class="size-value">{{ formatBytes(performanceMetrics.private_key_size) }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="size-info">
              <div class="size-label">
                {{ selectedTask.algorithm.category === 'KEM' ? '密文大小' : '签名大小' }}
              </div>
              <div class="size-value">
                {{ formatBytes(
                  selectedTask.algorithm.category === 'KEM' 
                    ? performanceMetrics.ciphertext_size 
                    : performanceMetrics.signature_size
                ) }}
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 详细结果表格 -->
      <el-card v-if="taskResults.length > 0">
        <template #header>
          <div class="card-header">
            <el-icon><Grid /></el-icon>
            <span>详细测试结果</span>
            <div class="header-actions">
              <el-button 
                type="primary" 
                size="small"
                @click="exportResults"
              >
                导出数据
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="paginatedResults" 
          v-loading="resultStore.loading"
          max-height="400"
        >
          <el-table-column prop="metric_name" label="指标名称" width="150" />
          <el-table-column prop="value" label="数值" width="120">
            <template #default="{ row }">
              {{ formatMetricValue(row.value) }}
            </template>
          </el-table-column>
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="test_round" label="测试轮次" width="100" />
          <el-table-column prop="created_at" label="时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <el-pagination
          v-if="taskResults.length > pageSize"
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="taskResults.length"
          layout="total, prev, pager, next"
          style="margin-top: 16px; text-align: center;"
        />
      </el-card>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button type="success" @click="generateReport">
          <el-icon><Document /></el-icon>
          生成PDF报告
        </el-button>
        <el-button type="info" @click="generateCSVReport">
          <el-icon><Download /></el-icon>
          导出CSV报告
        </el-button>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-else description="请选择一个已完成的任务来查看结果分析" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, InfoFilled, PieChart, Grid, Document, Download 
} from '@element-plus/icons-vue'
import { useTaskStore, useResultStore, useReportStore } from '@/stores'
import type { TestTask } from '@/api/tasks'
import type { TestResult, PerformanceMetrics } from '@/api/results'
import dayjs from 'dayjs'

// Stores
const taskStore = useTaskStore()
const resultStore = useResultStore()
const reportStore = useReportStore()

// 响应式数据
const filters = reactive({
  taskId: null as number | null,
})

const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const completedTasks = computed(() => taskStore.completedTasks)

const selectedTask = computed(() => {
  if (!filters.taskId) return null
  return taskStore.getTaskById(filters.taskId)
})

const taskResults = computed(() => {
  if (!filters.taskId) return []
  return resultStore.getTaskResults(filters.taskId)
})

const performanceMetrics = computed(() => {
  if (!filters.taskId) return null
  return resultStore.getTaskMetrics(filters.taskId)
})

const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return taskResults.value.slice(start, end)
})

// 方法
const formatDate = (dateStr: string | null) => {
  if (!dateStr) return 'N/A'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

const formatMetricValue = (value: number | undefined) => {
  if (value === undefined || value === null) return 'N/A'
  return value.toFixed(4)
}

const formatBytes = (bytes: number | undefined) => {
  if (!bytes) return 'N/A'
  
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const getExecutionDuration = () => {
  if (!selectedTask.value?.started_at || !selectedTask.value?.finished_at) {
    return 'N/A'
  }
  
  const start = dayjs(selectedTask.value.started_at)
  const end = dayjs(selectedTask.value.finished_at)
  const duration = end.diff(start, 'second')
  
  if (duration < 60) return `${duration} 秒`
  if (duration < 3600) return `${Math.floor(duration / 60)} 分 ${duration % 60} 秒`
  
  const hours = Math.floor(duration / 3600)
  const minutes = Math.floor((duration % 3600) / 60)
  return `${hours} 小时 ${minutes} 分`
}

const loadTaskResults = async () => {
  if (!filters.taskId) return
  
  try {
    await Promise.all([
      resultStore.fetchTaskResults(filters.taskId),
      resultStore.fetchTaskPerformanceMetrics(filters.taskId),
    ])
    currentPage.value = 1
  } catch (error) {
    ElMessage.error('加载任务结果失败')
  }
}

const exportResults = () => {
  if (!taskResults.value.length) return
  
  // 创建CSV内容
  const headers = ['指标名称', '数值', '单位', '测试轮次', '创建时间']
  const csvData = [
    headers.join(','),
    ...taskResults.value.map(result => [
      result.metric_name,
      result.value,
      result.unit || '',
      result.test_round || '',
      formatDate(result.created_at)
    ].map(field => `"${field}"`).join(','))
  ].join('\n')
  
  // 下载文件
  const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `task_${filters.taskId}_results.csv`
  link.click()
  
  ElMessage.success('结果数据已导出')
}

const generateReport = async () => {
  if (!filters.taskId) return
  
  try {
    await reportStore.generateReport(filters.taskId, 'pdf')
    ElMessage.success('PDF报告生成成功')
  } catch (error) {
    ElMessage.error('PDF报告生成失败')
  }
}

const generateCSVReport = async () => {
  if (!filters.taskId) return
  
  try {
    await reportStore.generateReport(filters.taskId, 'csv')
    ElMessage.success('CSV报告生成成功')
  } catch (error) {
    ElMessage.error('CSV报告生成失败')
  }
}

const refreshData = async () => {
  try {
    await taskStore.fetchTasks({ limit: 100 })
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  }
}

// 生命周期
onMounted(() => {
  taskStore.fetchTasks({ limit: 100 })
})
</script>

<style scoped>
.results-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-card {
  margin-bottom: 24px;
}

.results-content > .el-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
}

.metric-item {
  text-align: center;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fafafa;
}

.metric-item.success-rate {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-color: #67c23a;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 0.9rem;
  color: #666;
}

.size-info {
  text-align: center;
  padding: 12px;
}

.size-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 4px;
}

.size-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.action-buttons {
  text-align: center;
  margin-top: 24px;
}

.action-buttons .el-button {
  margin: 0 8px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .metric-item {
    margin-bottom: 16px;
  }
  
  .action-buttons .el-button {
    display: block;
    width: 100%;
    margin: 8px 0;
  }
}
</style>