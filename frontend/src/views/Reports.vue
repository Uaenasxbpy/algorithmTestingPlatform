<template>
  <div class="reports-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>报告中心</h2>
      <div class="header-actions">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="24" :sm="8">
        <el-card class="stats-card">
          <div class="stats-item">
            <el-icon class="stats-icon" color="#409eff"><Document /></el-icon>
            <div class="stats-content">
              <div class="stats-number">{{ totalReports }}</div>
              <div class="stats-label">总报告数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card class="stats-card">
          <div class="stats-item">
            <el-icon class="stats-icon" color="#67c23a"><Files /></el-icon>
            <div class="stats-content">
              <div class="stats-number">{{ pdfReports }}</div>
              <div class="stats-label">PDF 报告</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card class="stats-card">
          <div class="stats-item">
            <el-icon class="stats-icon" color="#e6a23c"><Collection /></el-icon>
            <div class="stats-content">
              <div class="stats-number">{{ csvReports }}</div>
              <div class="stats-label">CSV 报告</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 报告列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报告列表</span>
          <div class="header-actions">
            <el-dropdown @command="handleBatchAction">
              <el-button type="primary">
                批量操作
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="download">批量下载</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>批量删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <el-table 
        :data="reports" 
        v-loading="reportStore.loading"
        empty-text="暂无报告数据"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="report_name" label="报告名称" min-width="200">
          <template #default="{ row }">
            <div class="report-name">
              <el-icon>
                <document v-if="row.file_type === 'PDF'" />
                <collection v-else />
              </el-icon>
              <span>{{ row.report_name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="file_type" label="文件类型" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="row.file_type === 'PDF' ? 'success' : 'warning'"
              size="small"
            >
              {{ row.file_type }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="file_size" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        
        <el-table-column label="关联任务" width="150">
          <template #default="{ row }">
            <el-button 
              text 
              type="primary" 
              size="small"
              @click="viewTask(row.task_id)"
            >
              任务 #{{ row.task_id }}
            </el-button>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="生成时间" width="160" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button 
              text 
              type="primary" 
              size="small"
              @click="downloadReport(row)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            
            <el-button 
              text 
              type="success" 
              size="small"
              @click="previewReport(row)"
              v-if="row.file_type === 'PDF'"
            >
              <el-icon><View /></el-icon>
              预览
            </el-button>
            
            <el-button 
              text 
              type="danger" 
              size="small"
              @click="deleteReport(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- PDF预览对话框 -->
    <el-dialog
      v-model="showPreview"
      title="报告预览"
      width="80%"
    >
      <div class="pdf-preview">
        <iframe 
          v-if="previewUrl"
          :src="previewUrl"
          width="100%"
          height="600px"
          frameborder="0"
        ></iframe>
        <div v-else class="preview-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, Document, Files, Collection, ArrowDown, 
  Download, View, Delete, Loading 
} from '@element-plus/icons-vue'
import { useReportStore } from '@/stores'
import type { Report } from '@/api/reports'
import dayjs from 'dayjs'

// Store
const reportStore = useReportStore()

// 响应式数据
const selectedReports = ref<Report[]>([])
const showPreview = ref(false)
const previewUrl = ref('')

// 计算属性
const reports = computed(() => reportStore.reports)

const totalReports = computed(() => reports.value.length)

const pdfReports = computed(() => 
  reports.value.filter(report => report.file_type === 'PDF').length
)

const csvReports = computed(() => 
  reports.value.filter(report => report.file_type === 'CSV').length
)

// 方法
const formatDate = (dateStr: string) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

const formatFileSize = (size: number | undefined) => {
  if (!size) return 'N/A'
  
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

const refreshData = async () => {
  try {
    await reportStore.fetchAllReports()
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  }
}

const handleSelectionChange = (selection: Report[]) => {
  selectedReports.value = selection
}

const handleBatchAction = async (command: string) => {
  if (selectedReports.value.length === 0) {
    ElMessage.warning('请先选择要操作的报告')
    return
  }

  if (command === 'download') {
    // 批量下载
    for (const report of selectedReports.value) {
      downloadReport(report)
    }
  } else if (command === 'delete') {
    // 批量删除
    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${selectedReports.value.length} 个报告吗？此操作不可恢复。`,
        '确认批量删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )

      for (const report of selectedReports.value) {
        await reportStore.deleteReport(report.id)
      }
      
      ElMessage.success('批量删除成功')
      selectedReports.value = []
    } catch (error: any) {
      if (error !== 'cancel') {
        ElMessage.error('批量删除失败')
      }
    }
  }
}

const downloadReport = (report: Report) => {
  const downloadUrl = reportStore.getDownloadUrl(report.id)
  
  // 创建临时下载链接
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = report.report_name
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('开始下载报告')
}

const previewReport = (report: Report) => {
  if (report.file_type !== 'PDF') {
    ElMessage.warning('只能预览PDF格式的报告')
    return
  }
  
  previewUrl.value = reportStore.getPreviewUrl(report.id)
  showPreview.value = true
}

const closePreview = () => {
  showPreview.value = false
  previewUrl.value = ''
}

// 监听预览对话框关闭
watch(showPreview, (newVal) => {
  if (!newVal) {
    previewUrl.value = ''
  }
})

const deleteReport = async (report: Report) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除报告 "${report.report_name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await reportStore.deleteReport(report.id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewTask = (taskId: number) => {
  // 跳转到任务详情页
  window.open(`/tasks/${taskId}`, '_blank')
}

// 生命周期
onMounted(() => {
  reportStore.fetchAllReports()
})
</script>

<style scoped>
.reports-container {
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

.stats-row {
  margin-bottom: 24px;
}

.stats-card {
  height: 100px;
}

.stats-item {
  display: flex;
  align-items: center;
  height: 60px;
}

.stats-icon {
  font-size: 24px;
  margin-right: 16px;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pdf-preview {
  width: 100%;
  height: 600px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  gap: 12px;
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
  
  .stats-card {
    margin-bottom: 16px;
  }
}
</style>