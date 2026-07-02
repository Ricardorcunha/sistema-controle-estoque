import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboardAPI } from '../api/endpoints'
import Spinner from '../components/Spinner'

function StatCard({ icon, iconBg, iconColor, value, label }) {
  return (
    <div className="col-6 col-md-3">
      <div className="card shadow-sm h-100">
        <div className="card-body d-flex align-items-center gap-3">
          <div className={`icon-box ${iconBg}`}>
            <i className={`bi ${icon} ${iconColor}`}></i>
          </div>
          <div>
            <div className="fs-3 fw-bold text-dark">{value}</div>
            <div className="text-muted small">{label}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    dashboardAPI.get()
      .then(res => setData(res.data))
      .catch(() => setError('Erro ao carregar o dashboard.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />
  if (error) return <div className="alert alert-danger">{error}</div>

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h4 className="fw-bold mb-0">Dashboard</h4>
          <small className="text-muted">Visão geral do estoque</small>
        </div>
        <Link to="/movimentacoes/nova" className="btn btn-primary">
          <i className="bi bi-plus-lg me-1"></i> Nova Movimentação
        </Link>
      </div>

      {/* Cards de estatísticas */}
      <div className="row g-3 mb-4">
        <StatCard
          icon="bi-box-seam" iconBg="bg-primary bg-opacity-10" iconColor="text-primary"
          value={data.total_produtos} label="Produtos Ativos"
        />
        <StatCard
          icon="bi-arrow-down-circle" iconBg="bg-success bg-opacity-10" iconColor="text-success"
          value={data.entradas_hoje} label="Entradas Hoje"
        />
        <StatCard
          icon="bi-arrow-up-circle" iconBg="bg-danger bg-opacity-10" iconColor="text-danger"
          value={data.saidas_hoje} label="Saídas Hoje"
        />
        <StatCard
          icon="bi-exclamation-triangle" iconBg="bg-warning bg-opacity-10" iconColor="text-warning"
          value={data.produtos_criticos} label="Estoque Crítico"
        />
      </div>

      <div className="row g-3">
        {/* Últimas movimentações */}
        <div className="col-lg-7">
          <div className="card shadow-sm h-100">
            <div className="card-header bg-white d-flex justify-content-between align-items-center py-3">
              <h6 className="mb-0 fw-bold">
                <i className="bi bi-clock-history me-2 text-primary"></i>Últimas Movimentações
              </h6>
              <Link to="/movimentacoes" className="btn btn-sm btn-outline-primary">Ver todas</Link>
            </div>
            <div className="card-body p-0">
              {data.ultimas_movimentacoes?.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead className="table-light">
                      <tr><th>Produto</th><th>Tipo</th><th>Qtd</th><th>Data</th></tr>
                    </thead>
                    <tbody>
                      {data.ultimas_movimentacoes.map(mov => (
                        <tr key={mov.id}>
                          <td className="small fw-semibold">
                            {mov.produto_nome?.substring(0, 25) || '—'}
                          </td>
                          <td>
                            {mov.tipo === 'entrada'
                              ? <span className="badge bg-success"><i className="bi bi-arrow-down me-1"></i>Entrada</span>
                              : <span className="badge bg-danger"><i className="bi bi-arrow-up me-1"></i>Saída</span>
                            }
                          </td>
                          <td className="fw-bold">{mov.quantidade}</td>
                          <td className="small text-muted">
                            {new Date(mov.data).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-5 text-muted">
                  <i className="bi bi-inbox fs-1 d-block mb-2"></i>
                  Nenhuma movimentação registrada.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Produtos críticos */}
        <div className="col-lg-5">
          <div className="card shadow-sm h-100">
            <div className="card-header bg-white d-flex justify-content-between align-items-center py-3">
              <h6 className="mb-0 fw-bold">
                <i className="bi bi-exclamation-triangle me-2 text-warning"></i>Estoque Crítico
              </h6>
              <Link to="/produtos?status=critico" className="btn btn-sm btn-outline-warning">Ver todos</Link>
            </div>
            <div className="card-body p-0">
              {data.produtos_criticos_lista?.length > 0 ? (
                <ul className="list-group list-group-flush">
                  {data.produtos_criticos_lista.map(p => (
                    <li key={p.id} className="list-group-item d-flex justify-content-between align-items-center py-3">
                      <div>
                        <Link to={`/produtos/${p.id}`} className="fw-semibold small text-decoration-none">
                          {p.nome?.substring(0, 30)}
                        </Link>
                        <div className="text-muted" style={{ fontSize: '0.75rem' }}>
                          Mín: {p.quantidade_minima}
                        </div>
                      </div>
                      <span className={`badge rounded-pill ${p.quantidade_atual === 0 ? 'bg-danger' : 'bg-warning text-dark'}`}>
                        {p.quantidade_atual}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-5 text-muted">
                  <i className="bi bi-check-circle fs-1 d-block mb-2 text-success"></i>
                  Todos os produtos estão com estoque adequado!
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
