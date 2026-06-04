import axios from 'axios'
import { decrypt } from '../utils/crypto'

const api = axios.create({
  baseURL: 'http://localhost:8001',
  timeout: 10000,
})

// 响应拦截器：自动解密
api.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body.data === 'string') {
      try {
        response.data = JSON.parse(decrypt(body.data))
      } catch (e) {
        console.error('响应解密失败:', e)
      }
    }
    return response
  },
  (error) => Promise.reject(error)
)

// ---------- 系统管理 ----------
export const getPermissions = () => api.get('/api/system/permissions')
export const getRoles = () => api.get('/api/system/roles')
export const getRolePermissions = () => api.get('/api/system/role-permissions')
export const getUsers = () => api.get('/api/system/users')
export const getUserProfiles = () => api.get('/api/system/user-profiles')

// ---------- 门店管理 ----------
export const getProvinces = () => api.get('/api/stores/provinces')
export const getStores = () => api.get('/api/stores/')
export const getUserStores = () => api.get('/api/stores/user-stores')

// ---------- 课程管理 ----------
export const getCourseCategories = () => api.get('/api/courses/categories')
export const getCourses = () => api.get('/api/courses/')
export const getCourseFavorites = () => api.get('/api/courses/favorites')

// ---------- 动作库 ----------
export const getActionCategories = () => api.get('/api/actions/categories')
export const getActions = () => api.get('/api/actions/')
export const getActionFavorites = () => api.get('/api/actions/favorites')

// ---------- 标语 ----------
export const getSlogans = () => api.get('/api/slogans/')

// ---------- 赛事活动 ----------
export const getActivities = () => api.get('/api/activities/')

export default api
