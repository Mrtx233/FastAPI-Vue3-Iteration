import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getRoleFromToken, getRouteByRole } from '../api'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/admin', name: 'Admin', component: () => import('../views/AdminPage.vue'), meta: { roles: [1] } },
  { path: '/operator', name: 'Operator', component: () => import('../views/OperatorPage.vue'), meta: { roles: [2] } },
  { path: '/coach', name: 'Coach', component: () => import('../views/CoachPage.vue'), meta: { roles: [3] } },
  { path: '/member', name: 'Member', component: () => import('../views/MemberPage.vue'), meta: { roles: [4] } },
  { path: '/', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 导航守卫：未登录跳转登录，已登录校验角色权限
router.beforeEach((to, from, next) => {
  const token = getToken()

  // 登录页：已登录则跳回对应角色页
  if (to.name === 'Login') {
    if (token) {
      const roleId = getRoleFromToken()
      next({ name: getRouteByRole(roleId) })
    } else {
      next()
    }
    return
  }

  // 未登录：跳转登录页
  if (!token) {
    next({ name: 'Login' })
    return
  }

  // 已登录：校验角色是否匹配
  const roleId = getRoleFromToken()
  const allowedRoles = to.meta?.roles
  if (allowedRoles && !allowedRoles.includes(roleId)) {
    // 角色不匹配，跳转到自己角色的页面
    next({ name: getRouteByRole(roleId) })
    return
  }

  next()
})

export default router
