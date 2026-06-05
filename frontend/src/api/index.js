import axios from 'axios'
import { ElMessage } from 'element-plus'
import { decrypt } from '../utils/crypto'

// Token 管理（内存 + sessionStorage）
let token = sessionStorage.getItem('token') || ''

export function setToken(newToken) {
  token = newToken
  if (newToken) {
    sessionStorage.setItem('token', newToken)
  } else {
    sessionStorage.removeItem('token')
  }
}

export function getToken() {
  return token
}

export function clearToken() {
  setToken('')
}

const api = axios.create({
  baseURL: 'http://localhost:8001',
  timeout: 10000,
})

// 请求拦截器：自动带上 Authorization 头
api.interceptors.request.use((config) => {
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：自动解密 + 401 自动跳转登录
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
  (error) => {
    if (error.response) {
      const status = error.response.status
      if (status === 401) {
        clearToken()
        window.location.href = '/login'
      } else if (status === 403) {
        // 标记 silent403 的请求不弹提示（由调用方自行处理回退）
        if (!error.config?.silent403) {
          const detail = error.response.data?.detail || '权限不足'
          ElMessage.warning(detail)
        }
      }
    }
    return Promise.reject(error)
  }
)

// ---------- 登录 ----------
export const login = (username, password) =>
  api.post('/api/system/login', { username, password })

// ---------- 系统管理 ----------
export const getMe = () => api.get('/api/system/me')
export const getPermissions = (config) => api.get('/api/system/permissions', config)
export const getRoles = (config) => api.get('/api/system/roles', config)
export const getRolePermissions = (config) => api.get('/api/system/role-permissions', config)
export const getUsers = (config) => api.get('/api/system/users', config)
export const getUserProfiles = (config) => api.get('/api/system/user-profiles', config)

// 系统管理 CRUD
export const getUserById = (id) => api.get(`/api/system/users/${id}`)
export const getUserProfileByUserId = (userId) => api.get(`/api/system/user-profiles/by-user/${userId}`)
export const getPermissionById = (id) => api.get(`/api/system/permissions/${id}`)
export const getRoleById = (id) => api.get(`/api/system/roles/${id}`)
export const createUser = (data) => api.post('/api/system/users', data)
export const updateUser = (id, data) => api.put(`/api/system/users/${id}`, data)
export const deleteUser = (id) => api.delete(`/api/system/users/${id}`)
export const createPermission = (data) => api.post('/api/system/permissions', data)
export const updatePermission = (id, data) => api.put(`/api/system/permissions/${id}`, data)
export const deletePermission = (id) => api.delete(`/api/system/permissions/${id}`)
export const createRole = (data) => api.post('/api/system/roles', data)
export const updateRole = (id, data) => api.put(`/api/system/roles/${id}`, data)
export const deleteRole = (id) => api.delete(`/api/system/roles/${id}`)
export const createRolePermission = (data) => api.post('/api/system/role-permissions', data)
export const deleteRolePermission = (id) => api.delete(`/api/system/role-permissions/${id}`)
export const createUserProfile = (data) => api.post('/api/system/user-profiles', data)
export const updateUserProfile = (id, data) => api.put(`/api/system/user-profiles/${id}`, data)
export const deleteUserProfile = (id) => api.delete(`/api/system/user-profiles/${id}`)

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
export const getSloganById = (id) => api.get(`/api/slogans/${id}`)
export const createSlogan = (data) => api.post('/api/slogans/', data)
export const updateSlogan = (id, data) => api.put(`/api/slogans/${id}`, data)
export const deleteSlogan = (id) => api.delete(`/api/slogans/${id}`)

// ---------- 赛事活动 ----------
export const getActivities = () => api.get('/api/activities/')
export const getActivityById = (id) => api.get(`/api/activities/${id}`)
export const createActivity = (data) => api.post('/api/activities/', data)
export const updateActivity = (id, data) => api.put(`/api/activities/${id}`, data)
export const deleteActivity = (id) => api.delete(`/api/activities/${id}`)

export default api
