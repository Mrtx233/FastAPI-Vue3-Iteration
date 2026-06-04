import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'DataOverview', component: () => import('../views/DataOverview.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
