import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { movimentacoesAPI, produtosAPI } from '../../api/endpoints'
import Spinner from '../../components/Spinner'
import Pagination from '../../components/Pagination'

export default function MovimentacaoLista() {
  const [data, setData] = useState({ results: [], count: 0 })
  const [produtos, setProdutos] = useState([])
  const [loading, setLoading] = useState(true)
  const [tipo, setTipo] = useState('')
  const [produtoId, setProdutoId] = useState('')
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim] = useState('')
  const [page, setPage] = useState(1)

  useEffect(() => {
    produtosAPI.list({ page_size: 200, ativo: true })
      .then(res => setProdutos(res.data.results || []))
  }, [])

  const carregar = async () => {
    setLoading(true)
    try {
      const params = { page }
      if (tipo) params.tipo = tipo
      if (produtoId) params.produto = produtoId
      if (dataInicio) params.data_after = dataInicio
      if (dataFim) params.data_before = dataFim
      const res = await movimentacoesAPI.list(params)
      setData(res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { carregar() }, [tipo, produtoId, dataInicio, dataFim, page])

  const limpar = () => { setTipo(''); setProdutoId(''); setDataInicio(''); setDataFim(''); setPage(1) }
  const temFiltro = tipo || produtoId || dataInicio || dataFim

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">
          <i className="bi bi-arrow-left-right me-2 text-primary"></i>Movimentações
        </h4>
        <Link to="/movimentacoes/nova" className="btn btn-success">
          <i className="bi bi-plus-lg me-1"></i>Nova Movimentação
        </Link>
      </div>

      <div className="card shadow-sm">
        <div className="card-header bg-white py-3">
          <div className="row g-2 align-items-end">
            <div className="col-auto">
              <select className="form-select form-select-sm" style={{ minWidth: 130 }}
                value={tipo} onChange={e => { setTipo(e.target.value); setPage(1) }}>
                <option value="">Todos os tipos</option>
                <option value="entrada">Entrada</option>
                <option value="saida">Saída</option>
              </select>
            </div>
            <div className="col-auto">
              <select className="form-select form-select-sm" style={{ minWidth: 200 }}
                value={produtoId} onChange={e => { setProdutoId(e.target.value); setPage(1) }}>
                <option value="">Todos os produtos</option>
                {produtos.map(p => <option key={p.id} value={p.id}>{p.nome.substring(0, 30)}</option>)}
              </select>
            </div>
            <div className="col-auto">
              <input type="date" className="form-control form-control-sm" title="De"
                value={dataInicio} onChange={e => { setDataInicio(e.target.value); setPage(1) }} />
            </div>
            <div className="col-auto">
              <input type="date" className="form-control form-control-sm" title="Até"
                value={dataFim} onChange={e => { setDataFim(e.target.value); setPage(1) }} />
            </div>
            {temFiltro && (
              <div className="col-auto">
                <button className="btn btn-sm btn-outline-secondary" onClick={limpar}>Limpar</button>
              </div>
            )}
          </div>
        </div>

        {loading ? <Spinner /> : (
          <div className="table-responsive">
            <table className="table table-hover mb-0 align-middle">
              <thead className="table-light">
                <tr><th>#</th><th>Produto</th><th>Tipo</th><th className="text-center">Qtd</th><th>Usuário</th><th>Data</th><th>Observação</th></tr>
              </thead>
              <tbody>
                {data.results.length === 0 ? (
                  <tr><td colSpan={7} className="text-center py-5 text-muted">
                    <i className="bi bi-inbox fs-1 d-block mb-2"></i>Nenhuma movimentação encontrada.
                  </td></tr>
                ) : data.results.map(m => (
                  <tr key={m.id}>
                    <td className="text-muted small">{m.id}</td>
                    <td>
                      <Link to={`/produtos/${m.produto?.id || m.produto}`}
                        className="fw-semibold text-decoration-none small">
                        {(m.produto_nome || m.produto?.nome || '—').substring(0, 30)}
                      </Link>
                    </td>
                    <td>
                      {m.tipo === 'entrada'
                        ? <span className="badge bg-success"><i className="bi bi-arrow-down me-1"></i>Entrada</span>
                        : <span className="badge bg-danger"><i className="bi bi-arrow-up me-1"></i>Saída</span>}
                    </td>
                    <td className="text-center fw-bold">{m.quantidade}</td>
                    <td className="small">{m.usuario_nome || m.usuario}</td>
                    <td className="small text-muted">
                      {new Date(m.data).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="small text-muted">{m.observacao?.substring(0, 40) || '—'}</td>
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
