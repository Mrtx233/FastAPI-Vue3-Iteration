import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '../api'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/', name: 'DataOverview', component: () => import('../views/DataOverview.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 导航守卫：未登录时跳转登录页
router.beforeEach((to, from, next) => {
  const token = getToken()
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && token) {
    next({ name: 'DataOverview' })
  } else {
    next()
  }
})

export default router
