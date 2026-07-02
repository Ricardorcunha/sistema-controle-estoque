/**
 * AuthContext.jsx — Contexto global de autenticação.
 *
 * Provê para toda a aplicação:
 *   - user: dados do usuário logado (decodificado do JWT)
 *   - login(username, password): autentica e armazena os tokens
 *   - logout(): limpa tokens e redireciona para /login
 *   - loading: true enquanto verifica o token inicial (evita flash de tela)
 *
 * Os tokens ficam no localStorage para persistir entre recarregamentos.
 * (Para um SPA de portfólio, localStorage é aceitável.
 *  Em produção de alta segurança, prefira httpOnly cookies.)
 */

import { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../api/endpoints'

const AuthContext = createContext(null)

// Decodifica o payload do JWT (base64url) sem biblioteca externa
function decodeToken(token) {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Ao montar: verifica se há token salvo e tenta restaurar a sessão
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      const payload = decodeToken(token)
      if (payload && payload.exp * 1000 > Date.now()) {
        setUser(payload)
      } else {
        // Token expirado: limpa e deixa ir para login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    }
    setLoading(false)
  }, [])

  const login = async (username, password) => {
    const { data } = await authAPI.login(username, password)
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    const payload = decodeToken(data.access)
    setUser(payload)
    navigate('/', { replace: true })
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    navigate('/login', { replace: true })
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook customizado — uso: const { user, login, logout } = useAuth()
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth deve ser usado dentro de AuthProvider')
  return ctx
}
