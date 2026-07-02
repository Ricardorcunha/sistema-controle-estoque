import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { produtosAPI, categoriasAPI } from '../../api/endpoints'
import { useAuth } from '../../context/AuthContext'
import Spinner from '../../components/Spinner'
import Pagination from '../../components/Pagination'

function StatusBadge({ produto }) {
  if (!produto.ativo) return <span className="badge bg-secondary">Inativo</span>
  if (produto.quantidade_atual === 0) return <span className="badge bg-danger">Sem Estoque</span>
  if (produto.esta_abaixo_do_minimo) return <span className="badge bg-warning text-dark">Crítico</span>
  return <span className="badge bg-success">Normal</span>
}

export default function ProdutoLista() {
  const { user } = useAuth()
  const isAdmin = user?.perfil === 'admin' || user?.is_superuser
  const [searchParams] = useSearchParams()

  const [data, setData] = useState({ results: [], count: 0 })
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState('')
  const [status, setStatus] = useState(searchParams.get('status') || '')
  const [categoriaId, setCategoriaId] = useState('')
  const [page, setPage] = useState(1)
  const [msg, setMsg] = useState(null)

  useEffect(() => {
    categoriasAPI.list({ page_size: 100 })
      .then(res => setCategorias(res.data.results || []))
  }, [])

  const carregar = async () => {
    setLoading(true)
    try {
      const params = { page, search: q }
      if (status) params.status = status
      if (categoriaId) params.categoria = categoriaId
      const res = await produtosAPI.list(params)
      setData(res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { carregar() }, [q, status, categoriaId, page])

  const excluir = async (id, nome) => {
    if (!window.confirm(`Excluir o produto "${nome}"?`)) return
    try {
      await produtosAPI.delete(id)
      setMsg({ type: 'success', text: 'Produto excluído!' })
      carregar()
    } catch {
      setMsg({ type: 'danger', text: 'Não é possível excluir: há movimentações vinculadas.' })
    }
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">
          <i className="bi bi-box-seam me-2 text-primary"></i>Produtos
        </h4>
        {isAdmin && (
          <Link to="/produtos/novo" className="btn btn-primary">
            <i className="bi bi-plus-lg me-1"></i>Novo Produto
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
          <div className="d-flex gap-2 flex-wrap">
            <input type="text" className="form-control form-control-sm" placeholder="Buscar produto..."
              style={{ minWidth: 180 }} value={q}
              onChange={e => { setQ(e.target.value); setPage(1) }} />

            <select className="form-select form-select-sm" style={{ minWidth: 160 }}
              value={categoriaId} onChange={e => { setCategoriaId(e.target.value); setPage(1) }}>
              <option value="">Todas as categorias</option>
              {categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
            </select>

            <select className="form-select form-select-sm" style={{ minWidth: 140 }}
              value={status} onChange={e => { setStatus(e.target.value); setPage(1) }}>
              <option value="">Todos</option>
              <option value="ativo">Ativos</option>
              <option value="inativo">Inativos</option>
              <option value="critico">Estoque Crítico</option>
              <option value="sem_estoque">Sem Estoque</option>
            </select>

            {(q || status || categoriaId) && (
              <button className="btn btn-sm btn-outline-secondary"
                onClick={() => { setQ(''); setStatus(''); setCategoriaId(''); setPage(1) }}>
                Limpar
              </button>
            )}
          </div>
        </div>

        {loading ? <Spinner /> : (
          <div className="table-responsive">
            <table className="table table-hover mb-0 align-middle">
              <thead className="table-light">
                <tr>
                  <th>Produto</th><th>Categoria</th><th>Fornecedor</th>
                  <th className="text-end">Preço</th><th className="text-center">Qtd</th>
                  <th className="text-center">Status</th><th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {data.results.length === 0 ? (
                  <tr><td colSpan={7} className="text-center py-5 text-muted">
                    <i className="bi bi-inbox fs-1 d-block mb-2"></i>Nenhum produto encontrado.
                  </td></tr>
                ) : data.results.map(p => (
                  <tr key={p.id}>
                    <td>
                      <Link to={`/produtos/${p.id}`} className="fw-semibold text-decoration-none small">
                        {p.nome}
                      </Link>
                    </td>
                    <td className="small text-muted">{p.categoria_nome || p.categoria?.nome || '—'}</td>
                    <td className="small text-muted">{(p.fornecedor_nome || p.fornecedor?.nome || '—').substring(0, 20)}</td>
                    <td className="text-end small">R$ {Number(p.preco).toFixed(2)}</td>
                    <td className="text-center">
                      <span className={`fw-bold ${p.quantidade_atual === 0 ? 'text-danger' : p.esta_abaixo_do_minimo ? 'text-warning' : 'text-success'}`}>
                        {p.quantidade_atual}
                      </span>
                      <small className="text-muted d-block">mín: {p.quantidade_minima}</small>
                    </td>
                    <td className="text-center"><StatusBadge produto={p} /></td>
                    <td>
                      <Link to={`/produtos/${p.id}`} className="btn btn-sm btn-outline-primary me-1" title="Ver">
                        <i className="bi bi-eye"></i>
                      </Link>
                      {isAdmin && (
                        <>
                          <Link to={`/produtos/${p.id}/editar`} className="btn btn-sm btn-outline-secondary me-1" title="Editar">
                            <i className="bi bi-pencil"></i>
                          </Link>
                          <button className="btn btn-sm btn-outline-danger" title="Excluir" onClick={() => excluir(p.id, p.nome)}>
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
