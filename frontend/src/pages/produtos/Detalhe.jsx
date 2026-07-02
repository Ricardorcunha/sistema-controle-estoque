import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { produtosAPI } from '../../api/endpoints'
import { useAuth } from '../../context/AuthContext'
import Spinner from '../../components/Spinner'

export default function ProdutoDetalhe() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.perfil === 'admin' || user?.is_superuser

  const [produto, setProduto] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    produtosAPI.get(id)
      .then(res => setProduto(res.data))
      .catch(() => navigate('/produtos'))
      .finally(() => setLoading(false))
  }, [id])

  const excluir = async () => {
    if (!window.confirm(`Excluir o produto "${produto.nome}"?`)) return
    try {
      await produtosAPI.delete(id)
      navigate('/produtos')
    } catch {
      alert('Não é possível excluir: há movimentações vinculadas.')
    }
  }

  if (loading) return <Spinner />
  if (!produto) return null

  const qtdColor = produto.quantidade_atual === 0
    ? 'text-danger' : produto.esta_abaixo_do_minimo
    ? 'text-warning' : 'text-success'

  return (
    <>
      <div className="mb-3">
        <nav aria-label="breadcrumb">
          <ol className="breadcrumb small">
            <li className="breadcrumb-item"><Link to="/">Início</Link></li>
            <li className="breadcrumb-item"><Link to="/produtos">Produtos</Link></li>
            <li className="breadcrumb-item active">{produto.nome}</li>
          </ol>
        </nav>
      </div>

      <div className="d-flex justify-content-between align-items-start mb-4">
        <div>
          <h4 className="fw-bold mb-1">{produto.nome}</h4>
          <span className="text-muted small">ID #{produto.id} · {produto.categoria_nome || produto.categoria?.nome}</span>
        </div>
        {isAdmin && (
          <div className="d-flex gap-2">
            <Link to={`/movimentacoes/nova?produto=${produto.id}`} className="btn btn-success">
              <i className="bi bi-plus-lg me-1"></i>Movimentar
            </Link>
            <Link to={`/produtos/${produto.id}/editar`} className="btn btn-outline-secondary">
              <i className="bi bi-pencil me-1"></i>Editar
            </Link>
            <button className="btn btn-outline-danger" onClick={excluir}>
              <i className="bi bi-trash me-1"></i>Excluir
            </button>
          </div>
        )}
      </div>

      <div className="row g-3">
        <div className="col-md-5">
          <div className="card shadow-sm h-100">
            <div className="card-header bg-white py-3">
              <h6 className="mb-0 fw-bold"><i className="bi bi-info-circle me-2 text-primary"></i>Informações</h6>
            </div>
            <div className="card-body">
              <dl className="row mb-0 small">
                <dt className="col-5 text-muted">Status</dt>
                <dd className="col-7">
                  {produto.ativo
                    ? <span className="badge bg-success">Ativo</span>
                    : <span className="badge bg-secondary">Inativo</span>}
                </dd>
                <dt className="col-5 text-muted">Categoria</dt>
                <dd className="col-7">{produto.categoria_nome || produto.categoria?.nome}</dd>
                <dt className="col-5 text-muted">Fornecedor</dt>
                <dd className="col-7">{produto.fornecedor_nome || produto.fornecedor?.nome}</dd>
                <dt className="col-5 text-muted">Preço Unit.</dt>
                <dd className="col-7 fw-semibold">R$ {Number(produto.preco).toFixed(2)}</dd>
                <dt className="col-5 text-muted">Qtd. Mínima</dt>
                <dd className="col-7">{produto.quantidade_minima}</dd>
                <dt className="col-5 text-muted">Criado em</dt>
                <dd className="col-7">{new Date(produto.criado_em).toLocaleString('pt-BR')}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="col-md-7">
          <div className="row g-3 mb-3">
            <div className="col-6">
              <div className="card shadow-sm text-center py-3">
                <div className={`fs-1 fw-bold ${qtdColor}`}>{produto.quantidade_atual}</div>
                <div className="text-muted small">Estoque Atual</div>
              </div>
            </div>
            <div className="col-6">
              <div className="card shadow-sm text-center py-3">
                <div className="fs-3 fw-bold text-dark">
                  R$ {(produto.quantidade_atual * produto.preco).toFixed(2)}
                </div>
                <div className="text-muted small">Valor em Estoque</div>
              </div>
            </div>
          </div>

          <div className="card shadow-sm">
            <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h6 className="mb-0 fw-bold"><i className="bi bi-clock-history me-2 text-primary"></i>Últimas Movimentações</h6>
              <Link to={`/movimentacoes?produto=${produto.id}`} className="btn btn-sm btn-outline-primary">Ver todas</Link>
            </div>
            <div className="card-body p-0">
              {produto.movimentacoes?.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover mb-0 small">
                    <thead className="table-light"><tr><th>Tipo</th><th>Qtd</th><th>Usuário</th><th>Data</th></tr></thead>
                    <tbody>
                      {produto.movimentacoes.map(m => (
                        <tr key={m.id}>
                          <td>{m.tipo === 'entrada'
                            ? <span className="badge bg-success">Entrada</span>
                            : <span className="badge bg-danger">Saída</span>}
                          </td>
                          <td className="fw-bold">{m.quantidade}</td>
                          <td>{m.usuario_nome || m.usuario}</td>
                          <td className="text-muted">{new Date(m.data).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-4 text-muted">
                  <i className="bi bi-inbox d-block mb-2 fs-3"></i>Nenhuma movimentação.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
