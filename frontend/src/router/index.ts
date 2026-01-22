import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: { title: '首页' }
    },
    {
      path: '/algorithms',
      name: 'Algorithms',
      component: () => import('../views/Algorithms.vue'),
      meta: { title: '算法管理' }
    },
    {
      path: '/testing',
      name: 'Testing',
      component: () => import('../views/Testing.vue'),
      meta: { title: '性能测试' }
    },
    {
      path: '/results',
      name: 'Results',
      component: () => import('../views/Results.vue'),
      meta: { title: '结果分析' }
    },
    {
      path: '/reports',
      name: 'Reports',
      component: () => import('../views/Reports.vue'),
      meta: { title: '报告中心' }
    },
    {
      path: '/tasks/:id',
      name: 'TaskDetail',
      component: () => import('../views/TaskDetail.vue'),
      meta: { title: '任务详情' }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 算法测试平台`
  }
  next()
})

export default router