<template>
  <div id="app">
    <el-container class="layout-container">
      <!-- 左侧导航 -->
      <el-aside class="layout-aside">
        <div class="sidebar-content">
          <!-- Logo -->
          <div class="logo">
            <el-icon size="24"><Cpu /></el-icon>
            <span class="logo-text">算法测试平台</span>
          </div>
          
          <!-- 导航菜单 -->
          <nav class="nav-menu">
            <router-link 
              v-for="route in mainRoutes" 
              :key="route.path"
              :to="route.path"
              class="nav-item"
              :class="{ active: $route.path === route.path }"
            >
              <el-icon><component :is="route.icon" /></el-icon>
              <span>{{ route.name }}</span>
            </router-link>
          </nav>
        </div>
      </el-aside>

      <!-- 右侧内容区域 -->
      <el-container class="main-container">
        <!-- 顶部标题栏 -->
        <el-header class="layout-header">
          <div class="header-content">
            <h1 class="page-title">{{ getPageTitle() }}</h1>
            <div class="header-actions">
              <!-- 可以在这里添加其他操作按钮 -->
            </div>
          </div>
        </el-header>

        <!-- 主体内容 -->
        <el-main class="layout-main">
          <router-view />
        </el-main>

        <!-- 底部 -->
        <el-footer class="layout-footer">
          <div class="footer-content">
            <span>© 2025  PQC算法测试平台 - 后量子密码算法测试与验证</span>
          </div>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Cpu, Grid, CaretRight, PieChart, Document } from '@element-plus/icons-vue'

const route = useRoute()

const mainRoutes = [
  { path: '/', name: '首页', icon: 'Grid' },
  { path: '/algorithms', name: '算法管理', icon: 'Cpu' },
  { path: '/testing', name: '性能测试', icon: 'CaretRight' },
  { path: '/results', name: '结果分析', icon: 'PieChart' },
  { path: '/reports', name: '报告中心', icon: 'Document' },
]

// 获取当前页面标题
const getPageTitle = () => {
  const currentRoute = mainRoutes.find(r => r.path === route.path)
  return currentRoute ? currentRoute.name : '算法测试平台'
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

/* 左侧导航栏 */
.layout-aside {
  width: 240px !important;
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.sidebar-content {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 0;
}

/* Logo 区域 */
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  color: white;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 8px;
}

.logo-text {
  font-size: 16px;
}

/* 导航菜单 */
.nav-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 8px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 12px 24px;
  margin: 2px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-size: 14px;
}

.nav-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.nav-item.active {
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.nav-item .el-icon {
  font-size: 18px;
}

/* 右侧内容区域 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 顶部标题栏 */
.layout-header {
  background: white;
  border-bottom: 1px solid #e6e6e6;
  padding: 0;
  height: 60px !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 24px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 主体内容 */
.layout-main {
  background: #f5f5f5;
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 底部 */
.layout-footer {
  background: white;
  border-top: 1px solid #e6e6e6;
  height: 50px !important;
  padding: 0;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-size: 13px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .layout-aside {
    width: 200px !important;
  }
  
  .logo-text {
    font-size: 14px;
  }
  
  .nav-item {
    padding: 10px 16px;
    margin: 2px 8px;
  }
  
  .layout-main {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .layout-aside {
    width: 60px !important;
  }
  
  .logo-text,
  .nav-item span {
    display: none;
  }
  
  .logo {
    justify-content: center;
    padding: 16px 8px;
  }
  
  .nav-item {
    justify-content: center;
    padding: 12px 8px;
    margin: 2px 6px;
  }
  
  .header-content {
    padding: 0 16px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .layout-main {
    padding: 12px;
  }
}

/* 滚动条样式 */
.layout-main::-webkit-scrollbar {
  width: 6px;
}

.layout-main::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.layout-main::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.layout-main::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>