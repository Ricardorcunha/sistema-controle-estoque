/**
 * endpoints.js — Funções de acesso à API REST do Django.
 *
 * Organização por recurso. Cada função retorna a Promise do axios,
 * permitindo uso com async/await nas pages.
 */

import api from './client'

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authAPI = {
  login: (username, password) =>
    api.post('/auth/token/', { username, password }),

  refresh: (refresh) =>
    api.post('/auth/token/refresh/', { refresh }),

  verify: (token) =>
    api.post('/auth/token/verify/', { token }),
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const dashboardAPI = {
  get: () => api.get('/movimentacoes/dashboard/'),
}

// ── Categorias ────────────────────────────────────────────────────────────────
export const categoriasAPI = {
  list: (params) => api.get('/categorias/', { params }),
  get: (id) => api.get(`/categorias/${id}/`),
  create: (data) => api.post('/categorias/', data),
  update: (id, data) => api.put(`/categorias/${id}/`, data),
  delete: (id) => api.delete(`/categorias/${id}/`),
}

// ── Fornecedores ──────────────────────────────────────────────────────────────
export const fornecedoresAPI = {
  list: (params) => api.get('/fornecedores/', { params }),
  get: (id) => api.get(`/fornecedores/${id}/`),
  create: (data) => api.post('/fornecedores/', data),
  update: (id, data) => api.put(`/fornecedores/${id}/`, data),
  delete: (id) => api.delete(`/fornecedores/${id}/`),
}

// ── Produtos ──────────────────────────────────────────────────────────────────
export const produtosAPI = {
  list: (params) => api.get('/produtos/', { params }),
  get: (id) => api.get(`/produtos/${id}/`),
  create: (data) => api.post('/produtos/', data),
  update: (id, data) => api.put(`/produtos/${id}/`, data),
  delete: (id) => api.delete(`/produtos/${id}/`),
}

// ── Movimentações ─────────────────────────────────────────────────────────────
export const movimentacoesAPI = {
  list: (params) => api.get('/movimentacoes/', { params }),
  get: (id) => api.get(`/movimentacoes/${id}/`),
  create: (data) => api.post('/movimentacoes/', data),
  // Não há update/delete: movimentações são imutáveis
}
