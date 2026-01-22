<template>
  <div class="home-container">
    <!-- 欢迎标题 -->
    <div class="welcome-section">
      <h1 class="welcome-title">
        <el-icon size="32"><Cpu /></el-icon>
        欢迎使用算法测试平台
      </h1>
      <p class="welcome-subtitle">
        专业的后量子密码算法测试与验证平台，支持 NIST 标准化 PQC 算法性能评估
      </p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="24">
        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stats-card" :body-style="{ padding: '20px' }">
            <div class="stats-item">
              <div class="stats-icon algorithm">
                <el-icon size="24"><Cpu /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-number">{{ algorithmStats.total }}</div>
                <div class="stats-label">已注册算法</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stats-card" :body-style="{ padding: '20px' }">
            <div class="stats-item">
              <div class="stats-icon task">
                <el-icon size="24"><CaretRight /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-number">{{ taskStats.total }}</div>
                <div class="stats-label">测试任务</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stats-card" :body-style="{ padding: '20px' }">
            <div class="stats-item">
              <div class="stats-icon result">
                <el-icon size="24"><PieChart /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-number">{{ taskStats.completed }}</div>
                <div class="stats-label">已完成测试</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stats-card" :body-style="{ padding: '20px' }">
            <div class="stats-item">
              <div class="stats-icon report">
                <el-icon size="24"><Document /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-number">{{ reportStats.total }}</div>
                <div class="stats-label">生成报告</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>快捷操作</span>
          </div>
        </template>
        
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-button 
              type="primary" 
              size="large" 
              class="action-button"
              @click="$router.push('/algorithms')"
            >
              <el-icon><Cpu /></el-icon>
              管理算法
            </el-button>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-button 
              type="success" 
              size="large" 
              class="action-button"
              @click="$router.push('/testing')"
            >
              <el-icon><CaretRight /></el-icon>
              开始测试
            </el-button>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-button 
              type="warning" 
              size="large" 
              class="action-button"
              @click="$router.push('/results')"
            >
              <el-icon><PieChart /></el-icon>
              查看结果
            </el-button>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-button 
              type="info" 
              size="large" 
              class="action-button"
              @click="$router.push('/reports')"
            >
              <el-icon><Document /></el-icon>
              报告中心
            </el-button>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 最近任务 -->
    <el-row :gutter="24">
      <el-col :xs="24" :lg="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近测试任务</span>
              <el-button text type="primary" @click="$router.push('/testing')">
                查看全部
              </el-button>
            </div>
          </template>
          
          <el-table 
            :data="recentTasks" 
            v-loading="taskStore.loading"
            empty-text="暂无测试任务"
          >
            <el-table-column prop="task_name" label="任务名称" min-width="150" />
            <el-table-column prop="algorithm.name" label="算法" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag 
                  :type="getStatusType(row.status)"
                  size="small"
                >
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button 
                  text 
                  type="primary" 
                  size="small"
                  @click="$router.push(`/tasks/${row.id}`)"
                >
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>算法分类统计</span>
            </div>
          </template>
          
          <div class="algorithm-stats">
            <div class="stats-pie" ref="algorithmChartRef"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, nextTick } from 'vue'
import { Cpu, CaretRight, PieChart, Document } from '@element-plus/icons-vue'
import { useAlgorithmStore, useTaskStore, useReportStore } from '@/stores'
import dayjs from 'dayjs'

// Stores
const algorithmStore = useAlgorithmStore()
const taskStore = useTaskStore()
const reportStore = useReportStore()

// Refs
const algorithmChartRef = ref<HTMLDivElement>()

// 统计数据
const algorithmStats = computed(() => ({
  total: algorithmStore.algorithms.length,
  kem: algorithmStore.kemAlgorithms.length,
  signature: algorithmStore.signatureAlgorithms.length,
}))

const taskStats = computed(() => ({
  total: taskStore.tasks.length,
  pending: taskStore.pendingTasks.length,
  running: taskStore.runningTasks.length,
  completed: taskStore.completedTasks.length,
  failed: taskStore.failedTasks.length,
}))

const reportStats = computed(() => ({
  total: reportStore.reports.length,
}))

// 最近任务（取前5条）
const recentTasks = computed(() => 
  taskStore.tasks.slice(0, 5)
)

// 状态相关函数
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

const formatDate = (dateStr: string) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

// 初始化算法分类图表
const initAlgorithmChart = () => {
  if (!algorithmChartRef.value) return
  
  // 这里应该使用 ECharts 来渲染图表
  // 为了简化，暂时用文本显示
  algorithmChartRef.value.innerHTML = `
    <div style="text-align: center; padding: 20px;">
      <div style="margin-bottom: 16px;">
        <strong>KEM 算法: ${algorithmStats.value.kem}</strong>
      </div>
      <div>
        <strong>签名算法: ${algorithmStats.value.signature}</strong>
      </div>
    </div>
  `
}

// 组件挂载时获取数据
onMounted(async () => {
  try {
    await Promise.all([
      algorithmStore.fetchAlgorithms({ limit: 100 }),
      taskStore.fetchTasks({ limit: 20 }),
      reportStore.fetchAllReports({ limit: 100 })
    ])
    
    nextTick(() => {
      initAlgorithmChart()
    })
  } catch (error) {
    console.error('加载首页数据失败:', error)
  }
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.welcome-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
}

.stats-section {
  margin-bottom: 32px;
}

.stats-card {
  height: 120px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stats-item {
  display: flex;
  align-items: center;
  height: 80px;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  color: white;
}

.stats-icon.algorithm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.task {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.result {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.report {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
  line-height: 1;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 0.9rem;
  color: #666;
}

.quick-actions {
  margin-bottom: 32px;
}

.action-button {
  width: 100%;
  height: 60px;
  margin-bottom: 16px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.algorithm-stats {
  padding: 20px 0;
}

.stats-pie {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .welcome-title {
    font-size: 2rem;
  }
  
  .stats-card {
    margin-bottom: 16px;
  }
  
  .action-button {
    height: 48px;
    font-size: 14px;
  }
}
</style>