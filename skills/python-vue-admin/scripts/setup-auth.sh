#!/bin/bash
# setup-auth.sh - 快速配置 JWT 认证对接
# 在 frontend 目录运行

set -e

echo "🔐 配置 JWT 认证对接..."

npm install axios

cat > src/utils/http.ts << 'ENDOFFILE'
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const service: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 5000
})

service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = \`Bearer \${userStore.token}\`
    }
    return config
  },
  (error) => Promise.reject(error)
)

service.interceptors.response.use(
  (response) => {
    const { code, message, data } = response.data
    if (code === 200 || code === 0) return data
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message))
  },
  async (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      try {
        await userStore.refreshToken()
        return service(error.config)
      } catch {
        userStore.logout()
        window.location.href = '/login'
      }
    }
    ElMessage.error(error.response?.data?.message || '请求失败')
    return Promise.reject(error)
  }
)

export default service
ENDOFFILE

cat > src/api/system/auth.ts << 'ENDOFFILE'
import http from '@/utils/http'

export interface LoginReq {
  username: string
  password: string
}

export interface LoginRes {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RefreshReq {
  refresh_token: string
}

export const login = (data: LoginReq) =>
  http.request<LoginRes>('post', '/auth/login', { data })

export const refreshToken = (data: RefreshReq) =>
  http.request<LoginRes>('post', '/auth/refresh', { data })
ENDOFFILE

cat > src/stores/user.ts << 'ENDOFFILE'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, refreshToken as refreshTokenApi } from '@/api/system/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const refresh_token = ref<string>(localStorage.getItem('refresh_token') || '')

  async function login(username: string, password: string) {
    const res = await loginApi({ username, password })
    token.value = res.access_token
    refresh_token.value = res.refresh_token
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('refresh_token', res.refresh_token)
  }

  async function refreshToken() {
    try {
      const res = await refreshTokenApi({ refresh_token: refresh_token.value })
      token.value = res.access_token
      localStorage.setItem('token', res.access_token)
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    refresh_token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
  }

  return { token, refresh_token, login, refreshToken, logout }
})
ENDOFFILE

echo "✅ JWT 认证配置完成!"
echo "   - src/utils/http.ts"
echo "   - src/api/system/auth.ts"
echo "   - src/stores/user.ts"