import axios from 'axios'
import { decrypt } from '../utils/crypto'

const api = axios.create({
  baseURL: 'http://localhost:8001',
  timeout: 10000,
})

// 响应拦截器：自动解密整个响应体
api.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body.data === 'string') {
      try {
        const decrypted = decrypt(body.data)
        response.data = JSON.parse(decrypted)
      } catch (e) {
        console.error('响应解密失败:', e)
      }
    }
    return response
  },
  (error) => Promise.reject(error)
)

// ---------- 用户接口 ----------

export function getUsers(page = 1, pageSize = 10) {
  return api.get('/api/users', { params: { page, page_size: pageSize } })
}

export function getUserById(id) {
  return api.get(`/api/users/${id}`)
}

export function createUser(data) {
  return api.post('/api/users', data)
}

export function updateUser(id, data) {
  return api.put(`/api/users/${id}`, data)
}

export function deleteUser(id) {
  return api.delete(`/api/users/${id}`)
}

// ---------- 登录接口 ----------

export function login(data) {
  return api.post('/api/users/login', data)
}

export default api
