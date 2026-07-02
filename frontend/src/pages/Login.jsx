import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.username, form.password)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Usuário ou senha inválidos. Tente novamente.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center" style={{ background: '#f0f2f5' }}>
      <div className="w-100" style={{ maxWidth: 400 }}>
        {/* Logo */}
        <div className="text-center mb-4">
          <div
            className="rounded-circle bg-primary d-inline-flex align-items-center justify-content-center mb-3"
            style={{ width: 64, height: 64 }}
          >
            <i className="bi bi-box-seam text-white fs-3"></i>
          </div>
          <h4 className="fw-bold mb-0">Estoque Pro</h4>
          <p className="text-muted small">Sistema de Controle de Estoque</p>
        </div>

        <div className="card shadow-sm border-0">
          <div className="card-body p-4">
            <h5 className="fw-bold mb-4">Entrar</h5>

            {error && (
              <div className="alert alert-danger py-2 small">
                <i className="bi bi-exclamation-triangle me-2"></i>{error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label fw-semibold small">Usuário</label>
                <div className="input-group">
                  <span className="input-group-text"><i className="bi bi-person"></i></span>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="seu.usuario"
                    value={form.username}
                    onChange={(e) => setForm({ ...form, username: e.target.value })}
                    required
                    autoFocus
                  />
                </div>
              </div>

              <div className="mb-4">
                <label className="form-label fw-semibold small">Senha</label>
                <div className="input-group">
                  <span className="input-group-text"><i className="bi bi-lock"></i></span>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="••••••••"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary w-100"
                disabled={loading}
              >
                {loading
                  ? <><span className="spinner-border spinner-border-sm me-2"></span>Entrando...</>
                  : <><i className="bi bi-box-arrow-in-right me-2"></i>Entrar</>
                }
              </button>
            </form>
          </div>
        </div>

        <p className="text-center text-muted small mt-3">
          Sistema de portfólio — Django + React + JWT
        </p>
      </div>
    </div>
  )
}
