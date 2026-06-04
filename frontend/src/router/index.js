import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/users' },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/users', name: 'Users', component: () => import('../views/UserList.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
