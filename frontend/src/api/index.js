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

// 从 JWT 中获取角色 ID
export function getRoleFromToken() {
  try {
    if (!token) return null
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.role_id
  } catch { return null }
}

// 根据角色 ID 返回对应路由名
export function getRouteByRole(roleId) {
  switch (roleId) {
    case 1: return 'Admin'
    case 2: return 'Operator'
    case 3: return 'Coach'
    case 4: return 'Member'
    default: return 'Login'
  }
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
export const getProvinceById = (id) => api.get(`/api/stores/provinces/${id}`)
export const createProvince = (data) => api.post('/api/stores/provinces', data)
export const updateProvince = (id, data) => api.put(`/api/stores/provinces/${id}`, data)
export const deleteProvince = (id) => api.delete(`/api/stores/provinces/${id}`)
export const getStores = (config) => api.get('/api/stores/', config)
export const getStoreById = (storeId) => api.get(`/api/stores/${storeId}`)
export const createStore = (data) => api.post('/api/stores/', data)
export const updateStore = (id, data) => api.put(`/api/stores/${id}`, data)
export const deleteStore = (id) => api.delete(`/api/stores/${id}`)
export const getUserStores = () => api.get('/api/stores/user-stores')
export const getUserStoreById = (id) => api.get(`/api/stores/user-stores/${id}`)
export const getUserStoresByUserId = (userId) => api.get(`/api/stores/user-stores/by-user/${userId}`)
export const createUserStore = (data) => api.post('/api/stores/user-stores', data)
export const updateUserStore = (id, data) => api.put(`/api/stores/user-stores/${id}`, data)
export const deleteUserStore = (id) => api.delete(`/api/stores/user-stores/${id}`)

// ---------- 课程管理 ----------
export const getCourseCategories = () => api.get('/api/courses/categories')
export const getCourseCategoryById = (id) => api.get(`/api/courses/categories/${id}`)
export const createCourseCategory = (data) => api.post('/api/courses/categories', data)
export const updateCourseCategory = (id, data) => api.put(`/api/courses/categories/${id}`, data)
export const deleteCourseCategory = (id) => api.delete(`/api/courses/categories/${id}`)
export const getCourses = (config) => api.get('/api/courses/', config)
export const getCourseById = (id) => api.get(`/api/courses/${id}`)
export const getCoursesByCategory = (categoryId) => api.get(`/api/courses/category/${categoryId}`)
export const createCourse = (data) => api.post('/api/courses/', data)
export const updateCourse = (id, data) => api.put(`/api/courses/${id}`, data)
export const deleteCourse = (id) => api.delete(`/api/courses/${id}`)
export const getMyFavoriteCourses = () => api.get('/api/courses/favorites/me')
export const getCourseFavorites = () => api.get('/api/courses/favorites')
export const getCourseFavoriteById = (id) => api.get(`/api/courses/favorites/${id}`)
export const createCourseFavorite = (data) => api.post('/api/courses/favorites', data)
export const updateCourseFavorite = (id, data) => api.put(`/api/courses/favorites/${id}`, data)
export const deleteCourseFavorite = (id) => api.delete(`/api/courses/favorites/${id}`)

// ---------- 动作库 ----------
export const getActionCategories = () => api.get('/api/actions/categories')
export const getActionCategoryById = (id) => api.get(`/api/actions/categories/${id}`)
export const createActionCategory = (data) => api.post('/api/actions/categories', data)
export const updateActionCategory = (id, data) => api.put(`/api/actions/categories/${id}`, data)
export const deleteActionCategory = (id) => api.delete(`/api/actions/categories/${id}`)
export const getActions = (config) => api.get('/api/actions/', config)
export const getActionById = (id) => api.get(`/api/actions/${id}`)
export const getActionsByCategory = (categoryId) => api.get(`/api/actions/category/${categoryId}`)
export const createAction = (data) => api.post('/api/actions/', data)
export const updateAction = (id, data) => api.put(`/api/actions/${id}`, data)
export const deleteAction = (id) => api.delete(`/api/actions/${id}`)
export const getMyFavoriteActions = () => api.get('/api/actions/favorites/me')
export const getActionFavorites = () => api.get('/api/actions/favorites')
export const getActionFavoriteById = (id) => api.get(`/api/actions/favorites/${id}`)
export const createActionFavorite = (data) => api.post('/api/actions/favorites', data)
export const updateActionFavorite = (id, data) => api.put(`/api/actions/favorites/${id}`, data)
export const deleteActionFavorite = (id) => api.delete(`/api/actions/favorites/${id}`)

// ---------- 文件上传 ----------
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const listUploadedFiles = () => api.get('/api/upload/')
export const deleteUploadedFile = (filename) => api.delete(`/api/upload/${filename}`)

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
