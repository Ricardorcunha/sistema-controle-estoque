import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Spinner from './Spinner'

/**
 * ProtectedRoute — envolve rotas que exigem login.
 *
 * Enquanto o AuthContext está verificando o token salvo (loading=true),
 * exibe um spinner para evitar o flash de redirecionamento.
 * Após checar: se não há usuário, redireciona para /login.
 */
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) return <Spinner fullPage />
  if (!user) return <Navigate to="/login" replace />

  return children
}
