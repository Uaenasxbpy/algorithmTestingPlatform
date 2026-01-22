<template>
  <div class="testing-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>性能测试</h2>
      <div class="header-actions">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：创建测试 -->
      <el-col :xs="24" :lg="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><CaretRight /></el-icon>
              <span>创建新测试</span>
            </div>
          </template>
          
          <el-form
            ref="testFormRef"
            :model="testForm"
            :rules="testRules"
            label-width="100px"
            @submit.prevent="executeTest"
          >
            <el-form-item label="选择算法" prop="algorithm_id">
              <el-select 
                v-model="testForm.algorithm_id" 
                placeholder="请选择要测试的算法"
                @change="onAlgorithmChange"
                style="width: 100%"
              >
                <el-option-group label="KEM算法">
                  <el-option
                    v-for="alg in kemAlgorithms"
                    :key="alg.id"
                    :label="alg.name"
                    :value="alg.id"
                  >
                    <span>{{ alg.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                      {{ alg.source }}
                    </span>
                  </el-option>
                </el-option-group>
                
                <el-option-group label="签名算法">
                  <el-option
                    v-for="alg in signatureAlgorithms"
                    :key="alg.id"
                    :label="alg.name"
                    :value="alg.id"
                  >
                    <span>{{ alg.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                      {{ alg.source }}
                    </span>
                  </el-option>
                </el-option-group>
              </el-select>
            </el-form-item>
            
            <el-form-item label="测试名称" prop="test_name">
              <el-input 
                v-model="testForm.test_name" 
                placeholder="请输入测试名称"
              />
            </el-form-item>
            
            <el-form-item label="测试次数" prop="test_count">
              <el-input-number
                v-model="testForm.test_count"
                :min="1"
                :max="10000"
                :step="10"
                style="width: 100%"
              />
            </el-form-item>
            
            <!-- 高级参数 -->
            <el-form-item>
              <el-collapse v-model="showAdvanced">
                <el-collapse-item title="高级参数" name="advanced">
                  <el-form-item label="自定义参数">
                    <el-input
                      v-model="customParams"
                      type="textarea"
                      :rows="3"
                      placeholder="JSON格式的自定义参数，如：{&quot;threads&quot;: 4}"
                    />
                  </el-form-item>
                </el-collapse-item>
              </el-collapse>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="executeTest"
                :loading="executing"
                style="width: 100%"
                size="large"
              >
                <el-icon><CaretRight /></el-icon>
                开始测试
              </el-button>
            </el-form-item>
          </el-form>
          
          <!-- 算法信息展示 -->
          <div v-if="selectedAlgorithm" class="algorithm-info">
            <el-divider>算法信息</el-divider>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="算法名称">
                {{ selectedAlgorithm.name }}
              </el-descriptions-item>
              <el-descriptions-item label="算法类别">
                <el-tag :type="selectedAlgorithm.category === 'KEM' ? 'primary' : 'success'">
                  {{ selectedAlgorithm.category === 'KEM' ? 'KEM' : '签名算法' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="算法来源">
                {{ selectedAlgorithm.source }}
              </el-descriptions-item>
              <el-descriptions-item label="算法版本">
                {{ selectedAlgorithm.version || 'N/A' }}
              </el-descriptions-item>
              <el-descriptions-item label="算法描述">
                {{ selectedAlgorithm.description || '暂无描述' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：测试任务列表 -->
      <el-col :xs="24" :lg="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><list /></el-icon>
              <span>测试任务</span>
              <div class="header-actions">
                <el-dropdown @command="filterByStatus">
                  <span class="el-dropdown-link">
                    状态筛选
                    <el-icon><arrow-down /></el-icon>
                  </span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="">全部状态</el-dropdown-item>
                      <el-dropdown-item command="PENDING">待运行</el-dropdown-item>
                      <el-dropdown-item command="RUNNING">运行中</el-dropdown-item>
                      <el-dropdown-item command="COMPLETED">已完成</el-dropdown-item>
                      <el-dropdown-item command="FAILED">失败</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="displayTasks" 
            v-loading="taskStore.loading"
            empty-text="暂无测试任务"
            max-height="600"
          >
            <el-table-column prop="task_name" label="任务名称" min-width="150" />
            
            <el-table-column prop="algorithm.name" label="算法" width="120">
              <template #default="{ row }">
                <el-tag 
                  :type="row.algorithm.category === 'KEM' ? 'primary' : 'success'"
                  size="small"
                >
                  {{ row.algorithm.name }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="test_count" label="测试次数" width="80" />
            
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
            
            <!-- 进度条（仅运行中的任务显示） -->
            <el-table-column label="进度" width="120">
              <template #default="{ row }">
                <div v-if="row.status === 'RUNNING'" class="progress-info">
                  <el-progress 
                    :percentage="getTaskProgress(row.id)" 
                    :stroke-width="6"
                    :show-text="false"
                  />
                  <span class="progress-text">{{ getTaskProgress(row.id) }}%</span>
                </div>
                <span v-else-if="row.status === 'COMPLETED'" class="status-text success">
                  ✓ 完成
                </span>
                <span v-else-if="row.status === 'FAILED'" class="status-text error">
                  ✗ 失败
                </span>
              </template>
            </el-table-column>
            
            <el-table-column prop="created_at" label="创建时间" width="140">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button 
                  text 
                  type="primary" 
                  size="small"
                  @click="viewTaskDetail(row)"
                >
                  查看
                </el-button>
                
                <el-button 
                  v-if="row.status === 'PENDING'"
                  text 
                  type="success" 
                  size="small"
                  @click="runTask(row)"
                >
                  运行
                </el-button>
                
                <el-button 
                  v-if="row.status === 'RUNNING'"
                  text 
                  type="warning" 
                  size="small"
                  @click="stopTask(row)"
                >
                  停止
                </el-button>
                
                <el-button 
                  text 
                  type="danger" 
                  size="small"
                  @click="deleteTask(row)"
                  :disabled="row.status === 'RUNNING'"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CaretRight, Refresh, List, ArrowDown } from '@element-plus/icons-vue'
import { useAlgorithmStore, useTaskStore } from '@/stores'
import type { TestExecutionRequest } from '@/api/tasks'
import dayjs from 'dayjs'

// Stores
const algorithmStore = useAlgorithmStore()
const taskStore = useTaskStore()

// 响应式数据
const testFormRef = ref()
const executing = ref(false)
const showAdvanced = ref<string[]>([])
const customParams = ref('')
const statusFilter = ref('')

// 轮询定时器
let pollingTimer: NodeJS.Timeout | null = null

// 测试表单
const testForm = reactive<TestExecutionRequest>({
  algorithm_id: null as any,
  test_name: '',
  test_count: 100,
  parameters: {},
})

// 表单验证规则
const testRules = {
  algorithm_id: [
    { required: true, message: '请选择算法', trigger: 'change' },
  ],
  test_name: [
    { required: true, message: '请输入测试名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' },
  ],
  test_count: [
    { required: true, message: '请输入测试次数', trigger: 'blur' },
    { type: 'number', min: 1, max: 10000, message: '测试次数在 1 到 10000 之间', trigger: 'blur' },
  ],
}

// 计算属性
const kemAlgorithms = computed(() => 
  algorithmStore.activeAlgorithms.filter(alg => alg.category === 'KEM')
)

const signatureAlgorithms = computed(() => 
  algorithmStore.activeAlgorithms.filter(alg => alg.category === 'SIGNATURE')
)

const selectedAlgorithm = computed(() => 
  algorithmStore.getAlgorithmById(testForm.algorithm_id)
)

const displayTasks = computed(() => {
  let tasks = [...taskStore.tasks]
  
  if (statusFilter.value) {
    tasks = tasks.filter(task => task.status === statusFilter.value)
  }
  
  return tasks.sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
})

// 方法
const formatDate = (dateStr: string) => {
  return dayjs(dateStr).format('MM-DD HH:mm')
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

const getTaskProgress = (taskId: number) => {
  const status = taskStore.getTaskStatus(taskId)
  return status?.progress || 0
}

const onAlgorithmChange = () => {
  if (selectedAlgorithm.value) {
    testForm.test_name = `${selectedAlgorithm.value.name}_性能测试_${dayjs().format('YYYY-MM-DD_HH-mm')}`
  }
}

const executeTest = async () => {
  if (!testFormRef.value) return
  
  try {
    const valid = await testFormRef.value.validate()
    if (!valid) return
    
    executing.value = true
    
    // 解析自定义参数
    let parameters = {}
    if (customParams.value.trim()) {
      try {
        parameters = JSON.parse(customParams.value)
      } catch (error) {
        ElMessage.error('自定义参数格式错误，请使用有效的JSON格式')
        return
      }
    }
    
    const requestData = {
      ...testForm,
      parameters
    }
    
    await taskStore.executeTest(requestData)
    ElMessage.success('测试任务创建成功，正在后台执行')
    
    // 重置表单
    resetForm()
  } catch (error) {
    ElMessage.error('创建测试任务失败')
  } finally {
    executing.value = false
  }
}

const resetForm = () => {
  testForm.algorithm_id = null as any
  testForm.test_name = ''
  testForm.test_count = 100
  testForm.parameters = {}
  customParams.value = ''
  testFormRef.value?.resetFields()
}

const filterByStatus = (status: string) => {
  statusFilter.value = status
}

const viewTaskDetail = (task: any) => {
  taskStore.setCurrentTask(task)
  // 跳转到任务详情页
  window.open(`/tasks/${task.id}`, '_blank')
}

const stopTask = async (task: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要停止任务 "${task.task_name}" 吗？`,
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await taskStore.stopTask(task.id)
    ElMessage.success('任务已停止')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('停止任务失败')
    }
  }
}

const runTask = async (task: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要运行任务 "${task.task_name}" 吗？`,
      '确认运行',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    )
    
    // 调用手动运行任务API
    const response = await fetch(`http://localhost:8000/api/v1/tasks/${task.id}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (response.ok) {
      ElMessage.success('任务已开始运行')
      // 刷新任务列表
      await taskStore.fetchTasks({ limit: 50 })
    } else {
      const errorData = await response.json()
      ElMessage.error(errorData.detail || '运行任务失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('运行任务失败')
    }
  }
}

const deleteTask = async (task: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.task_name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await taskStore.deleteTask(task.id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const refreshData = async () => {
  try {
    await Promise.all([
      algorithmStore.fetchAlgorithms(),
      taskStore.fetchTasks({ limit: 50 })
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  }
}

// 轮询获取运行中任务的状态
const startPolling = () => {
  pollingTimer = setInterval(async () => {
    const runningTasks = taskStore.runningTasks
    if (runningTasks.length > 0) {
      for (const task of runningTasks) {
        try {
          await taskStore.fetchTaskStatus(task.id)
        } catch (error) {
          console.error('获取任务状态失败:', error)
        }
      }
    }
  }, 3000) // 每3秒轮询一次
}

const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 生命周期
onMounted(async () => {
  await refreshData()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.testing-container {
  max-width: 1400px;
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

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
}

.algorithm-info {
  margin-top: 24px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #666;
  min-width: 35px;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
}

.status-text.success {
  color: #67c23a;
}

.status-text.error {
  color: #f56c6c;
}

.el-dropdown-link {
  cursor: pointer;
  color: #409eff;
  display: flex;
  align-items: center;
  gap: 4px;
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
}
</style>