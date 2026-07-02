/**
 * client.js — Instância central do Axios.
 *
 * Responsabilidades:
 * 1. Prefixo base da API (/api/v1/)
 * 2. Interceptor de REQUEST: injeta o access token JWT no header Authorization
 * 3. Interceptor de RESPONSE: se receber 401, tenta renovar o token via refresh
 *    e reprocessa a requisição original. Se o refresh também falhar, desloga.
 *
 * Por que isso é importante para o portfólio?
 * → Demonstra conhecimento de autenticação stateless com JWT em SPAs.
 *   Em vez de redirecionar para login em cada 401, a renovação é transparente.
 */

import axios from 'axios'

const BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// ── Interceptor de REQUEST ────────────────────────────────────────────────────
// Adiciona o access token em toda requisição antes de enviá-la.
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Interceptor de RESPONSE ───────────────────────────────────────────────────
// Se a API retornar 401 (token expirado), tenta renovar automaticamente.
let isRefreshing = false
let failedQueue = []

// Enquanto o refresh está em andamento, acumula as requisições que falharam
// para reprocessá-las após o novo token chegar.
const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error)
    else prom.resolve(token)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Já há um refresh em andamento: enfileira esta requisição
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        // Sem refresh token: redireciona para login
        localStorage.clear()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        })
        localStorage.setItem('access_token', data.access)
        processQueue(null, data.access)
        originalRequest.headers.Authorization = `Bearer ${data.access}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.clear()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api
