<template>
  <div class="task-detail-container">
    <!-- 返回按钮 -->
    <div class="back-header">
      <el-button @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <div v-if="task" class="task-content">
      <!-- 任务基本信息 -->
      <el-card class="task-info-card">
        <template #header>
          <div class="card-header">
            <span>任务详情</span>
            <el-tag 
              :type="getStatusType(task.status)"
              size="large"
            >
              {{ getStatusText(task.status) }}
            </el-tag>
          </div>
        </template>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="任务名称">
                {{ task.task_name }}
              </el-descriptions-item>
              <el-descriptions-item label="算法名称">
                <el-tag :type="task.algorithm.category === 'KEM' ? 'primary' : 'success'">
                  {{ task.algorithm.name }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="算法类别">
                {{ task.algorithm.category === 'KEM' ? 'KEM (密钥封装)' : '数字签名' }}
              </el-descriptions-item>
              <el-descriptions-item label="测试次数">
                {{ task.test_count }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="创建时间">
                {{ formatDate(task.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatDate(task.started_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="完成时间">
                {{ formatDate(task.finished_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="执行时长">
                {{ getExecutionDuration() }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>

        <!-- 错误信息 -->
        <div v-if="task.error_message" class="error-message">
          <el-alert
            title="执行错误"
            type="error"
            :description="task.error_message"
            show-icon
            :closable="false"
          />
        </div>

        <!-- 实时进度（运行中任务） -->
        <div v-if="task.status === 'RUNNING'" class="progress-section">
          <el-divider>执行进度</el-divider>
          <el-progress 
            :percentage="taskProgress" 
            :stroke-width="20"
            :text-inside="true"
          />
          <p class="progress-text">任务正在执行中，请稍候...</p>
        </div>
      </el-card>

      <!-- 性能结果（已完成任务） -->
      <el-card v-if="task.status === 'COMPLETED' && performanceMetrics">
        <template #header>
          <div class="card-header">
            <span>性能指标</span>
          </div>
        </template>
        
        <el-row :gutter="16">
          <!-- KEM算法指标 -->
          <template v-if="task.algorithm.category === 'KEM'">
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-card">
                <div class="metric-title">密钥生成</div>
                <div class="metric-value">{{ formatTime(performanceMetrics.avg_keygen_time) }}</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-card">
                <div class="metric-title">封装时间</div>
                <div class="metric-value">{{ formatTime(performanceMetrics.avg_encaps_time) }}</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-card">
                <div class="metric-title">解封装时间</div>
                <div class="metric-value">{{ formatTime(performanceMetrics.avg_decaps_time) }}</div>
              </div>
            </el-col>
          </template>
          
          <!-- 签名算法指标 -->
          <template v-else>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-card">
                <div class="metric-title">密钥生成</div>
                <div class="metric-value">{{ formatTime(performanceMetrics.avg_keygen_time) }}</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-card">
                <div class="metric-title">签名时间</div>
                <div class="metric-value">{{ formatTime(performanceMetrics.avg_sign_time) }}</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :lg="6">
              <div class="metric-card">
                <div class="metric-title">验证时间</div>
                <div class="metric-value">{{ formatTime(performanceMetrics.avg_verify_time) }}</div>
              </div>
            </el-col>
          </template>
          
          <!-- 成功率 -->
          <el-col :xs="24" :sm="12" :lg="6">
            <div class="metric-card success-rate">
              <div class="metric-title">成功率</div>
              <div class="metric-value">{{ formatPercent(performanceMetrics.success_rate) }}</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 操作按钮 -->
      <div class="action-section">
        <el-button 
          v-if="task.status === 'RUNNING'"
          type="warning" 
          @click="stopTask"
        >
          <el-icon><VideoPlay /></el-icon>
          停止任务
        </el-button>
        
        <el-button 
          v-if="task.status === 'COMPLETED'"
          type="success" 
          @click="generatePDFReport"
        >
          <el-icon><Document /></el-icon>
          生成PDF报告
        </el-button>
        
        <el-button 
          v-if="task.status === 'COMPLETED'"
          type="info" 
          @click="generateCSVReport"
        >
          <el-icon><Download /></el-icon>
          导出CSV数据
        </el-button>
        
        <el-button 
          type="danger" 
          @click="deleteTask"
          :disabled="task.status === 'RUNNING'"
        >
          <el-icon><Delete /></el-icon>
          删除任务
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-container">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载任务详情中...</p>
    </div>

    <!-- 错误状态 -->
    <el-empty v-else description="任务不存在或加载失败" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, VideoPlay, Document, Download, Delete, Loading 
} from '@element-plus/icons-vue'
import { useTaskStore, useResultStore, useReportStore } from '@/stores'
import dayjs from 'dayjs'

// 路由
const route = useRoute()
const router = useRouter()

// Stores
const taskStore = useTaskStore()
const resultStore = useResultStore()
const reportStore = useReportStore()

// 响应式数据
const loading = ref(true)
const pollingTimer = ref<NodeJS.Timeout | null>(null)

// 计算属性
const taskId = computed(() => parseInt(route.params.id as string))

const task = computed(() => taskStore.currentTask || taskStore.getTaskById(taskId.value))

const performanceMetrics = computed(() => {
  if (!task.value || task.value.status !== 'COMPLETED') return null
  return resultStore.getTaskMetrics(task.value.id)
})

const taskProgress = computed(() => {
  if (!task.value) return 0
  const status = taskStore.getTaskStatus(task.value.id)
  return status?.progress || 0
})

// 方法
const formatDate = (dateStr: string | null) => {
  if (!dateStr) return 'N/A'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

const formatTime = (time: number | undefined | null) => {
  if (time === undefined || time === null) return 'N/A'
  return `${time.toFixed(4)} ms`
}

const formatPercent = (value: number | undefined | null) => {
  if (value === undefined || value === null) return 'N/A'
  return `${value.toFixed(2)}%`
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    'PENDING': 'info',
    'RUNNING': 'warning',
    'COMPLETED': 'success',
    'FAILED': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    'PENDING': '待运行',
    'RUNNING': '运行中',
    'COMPLETED': '已完成',
    'FAILED': '失败'
  }
  return textMap[status] || status
}

const getExecutionDuration = () => {
  if (!task.value?.started_at || !task.value?.finished_at) {
    return 'N/A'
  }
  
  const start = dayjs(task.value.started_at)
  const end = dayjs(task.value.finished_at)
  const duration = end.diff(start, 'second')
  
  if (duration < 60) return `${duration} 秒`
  if (duration < 3600) return `${Math.floor(duration / 60)} 分 ${duration % 60} 秒`
  
  const hours = Math.floor(duration / 3600)
  const minutes = Math.floor((duration % 3600) / 60)
  return `${hours} 小时 ${minutes} 分`
}

const goBack = () => {
  router.back()
}

const loadTaskData = async () => {
  try {
    loading.value = true
    
    // 获取任务详情
    await taskStore.fetchTask(taskId.value)
    
    // 如果任务已完成，获取性能指标
    if (task.value?.status === 'COMPLETED') {
      await resultStore.fetchTaskPerformanceMetrics(task.value.id)
    }
  } catch (error) {
    ElMessage.error('加载任务详情失败')
  } finally {
    loading.value = false
  }
}

const startPolling = () => {
  if (task.value?.status === 'RUNNING') {
    pollingTimer.value = setInterval(async () => {
      try {
        await taskStore.fetchTaskStatus(task.value!.id)
        
        // 如果任务完成，停止轮询并重新加载数据
        if (task.value!.status === 'COMPLETED' || task.value!.status === 'FAILED') {
          stopPolling()
          await loadTaskData()
        }
      } catch (error) {
        console.error('轮询任务状态失败:', error)
      }
    }, 2000)
  }
}

const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

const stopTask = async () => {
  if (!task.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要停止任务 "${task.value.task_name}" 吗？`,
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await taskStore.stopTask(task.value.id)
    ElMessage.success('任务已停止')
    await loadTaskData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('停止任务失败')
    }
  }
}

const generatePDFReport = async () => {
  if (!task.value) return
  
  try {
    await reportStore.generateReport(task.value.id, 'pdf')
    ElMessage.success('PDF报告生成成功')
  } catch (error) {
    ElMessage.error('PDF报告生成失败')
  }
}

const generateCSVReport = async () => {
  if (!task.value) return
  
  try {
    await reportStore.generateReport(task.value.id, 'csv')
    ElMessage.success('CSV报告生成成功')
  } catch (error) {
    ElMessage.error('CSV报告生成失败')
  }
}

const deleteTask = async () => {
  if (!task.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.value.task_name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await taskStore.deleteTask(task.value.id)
    ElMessage.success('删除成功')
    router.push('/testing')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 生命周期
onMounted(async () => {
  await loadTaskData()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.task-detail-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 16px;
}

.back-header {
  margin-bottom: 24px;
}

.task-content > .el-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-message {
  margin-top: 16px;
}

.progress-section {
  margin-top: 20px;
}

.progress-text {
  text-align: center;
  margin-top: 8px;
  color: #666;
  font-size: 14px;
}

.metric-card {
  text-align: center;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-card.success-rate {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-color: #67c23a;
}

.metric-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.action-section {
  text-align: center;
  margin-top: 24px;
}

.action-section .el-button {
  margin: 0 8px 8px 8px;
}

.loading-container {
  text-align: center;
  padding: 60px 0;
  color: #666;
}

.loading-container p {
  margin-top: 16px;
  font-size: 16px;
}

@media (max-width: 768px) {
  .task-detail-container {
    padding: 8px;
  }
  
  .action-section .el-button {
    display: block;
    width: 100%;
    margin: 8px 0;
  }
}
</style>