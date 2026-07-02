import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { categoriasAPI } from '../../api/endpoints'
import { useAuth } from '../../context/AuthContext'
import Spinner from '../../components/Spinner'
import Pagination from '../../components/Pagination'

export default function CategoriaLista() {
  const { user } = useAuth()
  const isAdmin = user?.perfil === 'admin' || user?.is_superuser

  const [data, setData] = useState({ results: [], count: 0 })
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)
  const [deletingId, setDeletingId] = useState(null)
  const [msg, setMsg] = useState(null)

  const carregar = async () => {
    setLoading(true)
    try {
      const res = await categoriasAPI.list({ search: q, page })
      setData(res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { carregar() }, [q, page])

  const excluir = async (id, nome) => {
    if (!window.confirm(`Excluir a categoria "${nome}"?`)) return
    try {
      await categoriasAPI.delete(id)
      setMsg({ type: 'success', text: 'Categoria excluída com sucesso!' })
      carregar()
    } catch (err) {
      const detail = err.response?.data?.detail || 'Não é possível excluir: há produtos vinculados.'
      setMsg({ type: 'danger', text: detail })
    }
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">
          <i className="bi bi-tags me-2 text-primary"></i>Categorias
        </h4>
        {isAdmin && (
          <Link to="/categorias/novo" className="btn btn-primary">
            <i className="bi bi-plus-lg me-1"></i>Nova Categoria
          </Link>
        )}
      </div>

      {msg && (
        <div className={`alert alert-${msg.type} alert-dismissible`}>
          {msg.text}
          <button type="button" className="btn-close" onClick={() => setMsg(null)}></button>
        </div>
      )}

      <div className="card shadow-sm">
        <div className="card-header bg-white py-3">
          <div className="d-flex gap-2">
            <input
              type="text" className="form-control form-control-sm"
              placeholder="Buscar por nome..." style={{ maxWidth: 300 }}
              value={q} onChange={e => { setQ(e.target.value); setPage(1) }}
            />
            {q && (
              <button className="btn btn-sm btn-outline-secondary" onClick={() => { setQ(''); setPage(1) }}>
                Limpar
              </button>
            )}
          </div>
        </div>

        {loading ? <Spinner /> : (
          <div className="table-responsive">
            <table className="table table-hover mb-0">
              <thead className="table-light">
                <tr><th>#</th><th>Nome</th><th>Descrição</th><th>Produtos</th><th>Ações</th></tr>
              </thead>
              <tbody>
                {data.results.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-5 text-muted">
                    <i className="bi bi-inbox fs-1 d-block mb-2"></i>Nenhuma categoria encontrada.
                  </td></tr>
                ) : data.results.map(cat => (
                  <tr key={cat.id}>
                    <td className="text-muted small">{cat.id}</td>
                    <td className="fw-semibold">{cat.nome}</td>
                    <td className="small text-muted">{cat.descricao?.substring(0, 50) || '—'}</td>
                    <td><span className="badge bg-primary rounded-pill">{cat.total_produtos ?? 0}</span></td>
                    <td>
                      {isAdmin && (
                        <>
                          <Link to={`/categorias/${cat.id}/editar`} className="btn btn-sm btn-outline-secondary me-1">
                            <i className="bi bi-pencil"></i>
                          </Link>
                          <button className="btn btn-sm btn-outline-danger" onClick={() => excluir(cat.id, cat.nome)}>
                            <i className="bi bi-trash"></i>
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && data.count > 0 && (
          <div className="card-footer bg-white">
            <Pagination count={data.count} page={page} onPageChange={setPage} />
          </div>
        )}
      </div>
    </>
  )
}
