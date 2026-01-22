<template>
  <div class="algorithms-container">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <h2>算法管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加算法
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card" :body-style="{ padding: '16px' }">
      <el-form :model="filters" inline>
        <el-form-item label="算法类别">
          <el-select v-model="filters.category" placeholder="全部类别" clearable>
            <el-option label="全部" value="" />
            <el-option label="KEM" value="KEM" />
            <el-option label="签名" value="SIGNATURE" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="算法来源">
          <el-select v-model="filters.source" placeholder="全部来源" clearable>
            <el-option label="全部" value="" />
            <el-option label="liboqs" value="liboqs" />
            <el-option label="PQClean" value="pqclean" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="filters.is_active" placeholder="全部状态" clearable>
            <el-option label="全部" value="" />
            <el-option label="激活" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 算法列表 -->
    <el-card>
      <el-table 
        :data="displayAlgorithms" 
        v-loading="algorithmStore.loading"
        empty-text="暂无算法数据"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" label="算法名称" min-width="150" sortable="custom">
          <template #default="{ row }">
            <div class="algorithm-name">
              <el-icon><Cpu /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="category" label="类别" width="100">
          <template #default="{ row }">
            <el-tag :type="row.category === 'KEM' ? 'primary' : 'success'" size="small">
              {{ row.category === 'KEM' ? 'KEM' : '签名' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="source" label="来源" width="100" />
        <el-table-column prop="version" label="版本" width="100" />
        
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="handleStatusChange(row)"
              :loading="row.updating"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160" sortable="custom">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="testAlgorithm(row)">
              <el-icon><Tools /></el-icon>
              测试
            </el-button>
            <el-button text type="primary" size="small" @click="validateConfig(row)">
              <el-icon><CircleCheck /></el-icon>
              验证配置
            </el-button>
            <el-button text type="primary" size="small" @click="editAlgorithm(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button text type="danger" size="small" @click="deleteAlgorithm(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑算法对话框 -->
    <!-- 添加/编辑算法对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingAlgorithm ? '编辑算法' : '添加算法'"
      width="600px"
      @closed="resetForm"
    >
      <el-form
        ref="algorithmFormRef"
        :model="algorithmForm"
        :rules="algorithmRules"
        label-width="100px"
      >
        <el-form-item label="算法名称" prop="name">
          <el-input v-model="algorithmForm.name" placeholder="请输入算法名称（如：Kyber512、Dilithium2）" />
          <div class="form-help-text">
            <div class="help-title">常见后量子密码算法名称示例：</div>
            <div class="algorithm-examples">
              <div class="example-title">KEM算法：</div>
              <div class="example-item">• Kyber512, Kyber768, Kyber1024</div>
              <div class="example-item">• NTRU-HPS-2048-509, NTRU-HPS-2048-677</div>
              <div class="example-item">• SABER-KEM-128s, SABER-KEM-192f, SABER-KEM-256f</div>
              <div class="example-title">签名算法：</div>
              <div class="example-item">• Dilithium2, Dilithium3, Dilithium5</div>
              <div class="example-item">• Falcon-512, Falcon-1024</div>
              <div class="example-item">• SPHINCS+-SHAKE256-128s, SPHINCS+-SHA256-192f</div>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="算法类别" prop="category">
          <el-radio-group v-model="algorithmForm.category">
            <el-radio label="KEM">KEM (密钥封装)</el-radio>
            <el-radio label="SIGNATURE">SIGNATURE (数字签名)</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="算法来源" prop="source">
          <el-select v-model="algorithmForm.source" placeholder="请选择算法来源">
            <el-option label="liboqs" value="liboqs" />
            <el-option label="PQClean" value="pqclean" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="版本号" prop="version">
          <el-input v-model="algorithmForm.version" placeholder="请输入版本号（如：1.0、1.2.3）" />
          <div class="form-help-text">
            版本号格式：x.y 或 x.y.z（如：1.0、1.2.3）
          </div>
        </el-form-item>
        
        <el-form-item label="库函数名" prop="library_name">
          <el-input 
            v-model="algorithmForm.library_name" 
            :placeholder="getLibraryNamePlaceholder()"
          />
          <div class="form-help-text">
            <template v-if="algorithmForm.source === 'liboqs'">
              <div class="help-title">liboqs 库函数名命名规范：</div>
              <div class="algorithm-examples">
                <div class="example-title">KEM算法：</div>
                <div class="example-item">• OQS_KEM_kyber_512、OQS_KEM_kyber_768</div>
                <div class="example-item">• OQS_KEM_ntru_hps2048509、OQS_KEM_ntru_hps2048677</div>
                <div class="example-title">签名算法：</div>
                <div class="example-item">• OQS_SIG_dilithium_2、OQS_SIG_dilithium_3</div>
                <div class="example-item">• OQS_SIG_falcon_512、OQS_SIG_falcon_1024</div>
              </div>
            </template>
            <template v-else-if="algorithmForm.source === 'pqclean'">
              <div class="help-title">PQClean 库函数名命名规范：</div>
              <div class="algorithm-examples">
                <div class="example-title">KEM算法：</div>
                <div class="example-item">• PQCLEAN_KYBER512_CLEAN、PQCLEAN_KYBER768_CLEAN</div>
                <div class="example-item">• PQCLEAN_NTRUHPS2048509_CLEAN</div>
                <div class="example-title">签名算法：</div>
                <div class="example-item">• PQCLEAN_DILITHIUM2_CLEAN、PQCLEAN_DILITHIUM3_CLEAN</div>
                <div class="example-item">• PQCLEAN_FALCON512_CLEAN、PQCLEAN_FALCON1024_CLEAN</div>
              </div>
            </template>
            <template v-else>
              <div class="help-title">请输入C库中的函数名前缀</div>
              <div class="form-help-text">确保函数名与实际的C库函数名称一致</div>
            </template>
          </div>
        </el-form-item>
        
        <el-form-item label="算法描述" prop="description">
          <el-input
            v-model="algorithmForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入算法描述"
          />
        </el-form-item>
        
        <!-- 算法测试指导信息 -->
        <el-alert
          title="算法测试指导"
          type="info"
          :closable="false"
          style="margin-top: 16px;"
        >
          <template #default>
            <div class="test-guide">
              <p><strong>为确保算法能正常通过后端测试，请注意以下要点：</strong></p>
              <ul>
                <li><strong>算法名称：</strong>必须与实际算法标准名称一致</li>
                <li><strong>库函数名：</strong>必须与实际C库中的函数名称完全匹配</li>
                <li><strong>算法类别：</strong>选择正确的类别（KEM或SIGNATURE）</li>
                <li><strong>算法来源：</strong>选择正确的来源库（liboqs、pqclean或其他）</li>
              </ul>
              <p><strong>建议：</strong>在添加算法前，请先点击“验证配置”按钮检查配置是否正确。</p>
            </div>
          </template>
        </el-alert>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button 
            type="info" 
            @click="validateCurrentConfig" 
            :loading="validating"
            v-if="!editingAlgorithm"
          >
            <el-icon><CircleCheck /></el-icon>
            验证配置
          </el-button>
          <el-button type="primary" @click="saveAlgorithm" :loading="saving">
            <el-icon><Check /></el-icon>
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Cpu, Tools, CircleCheck, Edit, Delete, Check } from '@element-plus/icons-vue'
import { useAlgorithmStore } from '@/stores'
import type { Algorithm, AlgorithmCreate, AlgorithmUpdate } from '@/api/algorithms'
import dayjs from 'dayjs'

// Store
const algorithmStore = useAlgorithmStore()

// 响应式数据
const showAddDialog = ref(false)
const editingAlgorithm = ref<Algorithm | null>(null)
const saving = ref(false)
const validating = ref(false)
const algorithmFormRef = ref()

// 筛选条件
const filters = reactive({
  category: '',
  source: '',
  is_active: '',
})

// 排序条件
const sort = reactive({
  prop: '',
  order: '',
})

// 算法表单
const algorithmForm = reactive<AlgorithmCreate>({
  name: '',
  category: 'KEM',
  source: 'liboqs',
  version: '',
  description: '',
  library_name: '',
})

// 表单验证规则
const algorithmRules = {
  name: [
    { required: true, message: '请输入算法名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_+-]+$/, message: '算法名称只能包含字母、数字、下划线、加号和减号', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择算法类别', trigger: 'change' },
  ],
  source: [
    { required: true, message: '请选择算法来源', trigger: 'change' },
  ],
  library_name: [
    { required: true, message: '请输入库函数名', trigger: 'blur' },
    { min: 3, max: 100, message: '库函数名长度在 3 到 100 个字符', trigger: 'blur' },
    { 
      validator: (rule: any, value: string, callback: any) => {
        if (algorithmForm.source === 'liboqs' && !value.startsWith('OQS_')) {
          callback(new Error('liboqs 算法的库函数名应以 OQS_ 开头'))
        } else if (algorithmForm.source === 'pqclean' && !value.startsWith('PQCLEAN_')) {
          callback(new Error('PQClean 算法的库函数名应以 PQCLEAN_ 开头'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^\d+\.\d+(\.\d+)?$/, message: '版本号格式应为 x.y 或 x.y.z', trigger: 'blur' }
  ]
}

// 计算属性 - 显示的算法列表
const displayAlgorithms = computed(() => {
  let algorithms = [...algorithmStore.algorithms]
  
  // 应用筛选
  if (filters.category) {
    algorithms = algorithms.filter(alg => alg.category === filters.category)
  }
  if (filters.source) {
    algorithms = algorithms.filter(alg => alg.source === filters.source)
  }
  if (filters.is_active !== '') {
    algorithms = algorithms.filter(alg => alg.is_active === filters.is_active)
  }
  
  // 应用排序
  if (sort.prop && sort.order) {
    algorithms.sort((a, b) => {
      let aVal = a[sort.prop as keyof Algorithm]
      let bVal = b[sort.prop as keyof Algorithm]
      
      if (sort.prop === 'created_at') {
        aVal = new Date(aVal as string).getTime()
        bVal = new Date(bVal as string).getTime()
      }
      
      if (sort.order === 'ascending') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })
  }
  
  return algorithms
})

// 方法
const formatDate = (dateStr: string) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

const refreshData = async () => {
  try {
    await algorithmStore.fetchAlgorithms()
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  }
}

const handleFilter = () => {
  // 筛选逻辑已在 computed 中处理
}

const resetFilters = () => {
  filters.category = ''
  filters.source = ''
  filters.is_active = ''
}

const handleSortChange = ({ prop, order }: any) => {
  sort.prop = prop
  sort.order = order
}

const handleStatusChange = async (algorithm: Algorithm) => {
  algorithm.updating = true
  try {
    await algorithmStore.updateAlgorithm(algorithm.id, {
      is_active: algorithm.is_active
    })
    ElMessage.success('状态更新成功')
  } catch (error) {
    // 回滚状态
    algorithm.is_active = !algorithm.is_active
    ElMessage.error('状态更新失败')
  } finally {
    algorithm.updating = false
  }
}

const testAlgorithm = async (algorithm: Algorithm) => {
  try {
    const result = await algorithmStore.testAlgorithm(algorithm.id)
    if (result.success) {
      ElMessage.success('算法测试成功')
    } else {
      ElMessage.warning(`算法测试失败: ${result.message || '未知错误'}`)
    }
  } catch (error: any) {
    ElMessage.error(`算法测试出错: ${error.message || '网络错误'}`)
  }
}

// 验证算法配置
const validateConfig = async (algorithm: Algorithm) => {
  try {
    ElMessage.info('正在验证算法配置...')
    const result = await validateAlgorithmConfig(algorithm)
    
    if (result.valid) {
      ElMessage.success('算法配置验证成功')
    } else {
      ElMessage.warning(`算法配置验证失败: ${result.message}`)
    }
  } catch (error: any) {
    ElMessage.error(`验证配置出错: ${error.message || '网络错误'}`)
  }
}

// 验证当前表单配置
const validateCurrentConfig = async () => {
  if (!algorithmFormRef.value) return
  
  try {
    const valid = await algorithmFormRef.value.validate()
    if (!valid) {
      ElMessage.warning('请先填写完所有必填项')
      return
    }
    
    validating.value = true
    ElMessage.info('正在验证算法配置...')
    
    const result = await validateAlgorithmConfig(algorithmForm as Algorithm)
    
    if (result.valid) {
      ElMessage.success('算法配置验证成功，可以安全添加')
    } else {
      ElMessage.warning(`算法配置验证失败: ${result.message}`)
    }
  } catch (error: any) {
    ElMessage.error(`验证配置出错: ${error.message || '网络错误'}`)
  } finally {
    validating.value = false
  }
}

const editAlgorithm = (algorithm: Algorithm) => {
  editingAlgorithm.value = algorithm
  Object.assign(algorithmForm, {
    name: algorithm.name,
    category: algorithm.category,
    source: algorithm.source,
    version: algorithm.version || '',
    description: algorithm.description || '',
    library_name: algorithm.library_name || '',
  })
  showAddDialog.value = true
}

const deleteAlgorithm = async (algorithm: Algorithm) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除算法 "${algorithm.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await algorithmStore.deleteAlgorithm(algorithm.id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveAlgorithm = async () => {
  if (!algorithmFormRef.value) return
  
  try {
    const valid = await algorithmFormRef.value.validate()
    if (!valid) return
    
    saving.value = true
    
    // 检查算法名称是否重复
    if (!editingAlgorithm.value) {
      const existingAlgorithm = algorithmStore.algorithms.find(
        alg => alg.name.toLowerCase() === algorithmForm.name.toLowerCase()
      )
      if (existingAlgorithm) {
        ElMessage.error('算法名称已存在，请使用不同的名称')
        saving.value = false
        return
      }
    }
    
    if (editingAlgorithm.value) {
      // 编辑模式
      await algorithmStore.updateAlgorithm(editingAlgorithm.value.id, algorithmForm)
      ElMessage.success('更新成功')
    } else {
      // 添加模式
      await algorithmStore.createAlgorithm(algorithmForm)
      ElMessage.success('添加成功')
    }
    
    showAddDialog.value = false
  } catch (error) {
    ElMessage.error(editingAlgorithm.value ? '更新失败' : '添加失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  editingAlgorithm.value = null
  Object.assign(algorithmForm, {
    name: '',
    category: 'KEM',
    source: 'liboqs',
    version: '',
    description: '',
    library_name: '',
  })
  algorithmFormRef.value?.resetFields()
}

// 获取库函数名占位符
const getLibraryNamePlaceholder = () => {
  if (algorithmForm.source === 'liboqs') {
    return '请输入库函数名（如：OQS_KEM_kyber_512）'
  } else if (algorithmForm.source === 'pqclean') {
    return '请输入库函数名（如：PQCLEAN_KYBER512_CLEAN）'
  } else {
    return '请输入C库中的函数名前缀'
  }
}

// 验证算法配置
const validateAlgorithmConfig = async (algorithm: Algorithm) => {
  try {
    // 这里可以调用后端API验证算法配置
    const response = await fetch(`/api/v1/algorithms/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: algorithm.name,
        category: algorithm.category,
        source: algorithm.source,
        library_name: algorithm.library_name,
        version: algorithm.version,
      }),
    })
    
    const result = await response.json()
    return result
  } catch (error) {
    console.error('验证算法配置失败:', error)
    return { valid: false, message: '验证服务不可用' }
  }
}

// 组件挂载时获取数据
onMounted(() => {
  algorithmStore.fetchAlgorithms()
})
</script>

<style scoped>
.algorithms-container {
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

.algorithm-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-help-text {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.form-help-text .help-title {
  font-weight: 500;
  color: #606266;
  margin-bottom: 2px;
}

.algorithm-examples {
  margin-top: 8px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
}

.algorithm-examples .example-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.algorithm-examples .example-item {
  margin: 2px 0;
  padding-left: 8px;
}

.test-guide {
  font-size: 14px;
  line-height: 1.6;
}

.test-guide ul {
  margin: 8px 0;
  padding-left: 20px;
}

.test-guide li {
  margin: 4px 0;
}

.test-guide strong {
  color: #409eff;
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
  
  .dialog-footer {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>