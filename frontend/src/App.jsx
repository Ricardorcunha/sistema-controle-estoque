import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'

import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import CategoriaLista from './pages/categorias/Lista'
import CategoriaForm from './pages/categorias/Form'
import FornecedorLista from './pages/fornecedores/Lista'
import FornecedorForm from './pages/fornecedores/Form'
import ProdutoLista from './pages/produtos/Lista'
import ProdutoDetalhe from './pages/produtos/Detalhe'
import ProdutoForm from './pages/produtos/Form'
import MovimentacaoLista from './pages/movimentacoes/Lista'
import MovimentacaoForm from './pages/movimentacoes/Form'

export default function App() {
  const { user } = useAuth()

  return (
    <Routes>
      {/* Rota pública */}
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />

      {/* Rotas protegidas — todas dentro do Layout */}
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<Dashboard />} />

        <Route path="/categorias" element={<CategoriaLista />} />
        <Route path="/categorias/novo" element={<CategoriaForm />} />
        <Route path="/categorias/:id/editar" element={<CategoriaForm />} />

        <Route path="/fornecedores" element={<FornecedorLista />} />
        <Route path="/fornecedores/novo" element={<FornecedorForm />} />
        <Route path="/fornecedores/:id/editar" element={<FornecedorForm />} />

        <Route path="/produtos" element={<ProdutoLista />} />
        <Route path="/produtos/novo" element={<ProdutoForm />} />
        <Route path="/produtos/:id" element={<ProdutoDetalhe />} />
        <Route path="/produtos/:id/editar" element={<ProdutoForm />} />

        <Route path="/movimentacoes" element={<MovimentacaoLista />} />
        <Route path="/movimentacoes/nova" element={<MovimentacaoForm />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
