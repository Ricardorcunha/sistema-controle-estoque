import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { movimentacoesAPI, produtosAPI } from '../../api/endpoints'
import Spinner from '../../components/Spinner'

export default function MovimentacaoForm() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [produtos, setProdutos] = useState([])
  const [produtoAtual, setProdutoAtual] = useState(null)
  const [form, setForm] = useState({
    produto: searchParams.get('produto') || '',
    tipo: 'entrada',
    quantidade: '',
    observacao: '',
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})

  // Carrega lista de produtos
  useEffect(() => {
    produtosAPI.list({ page_size: 200, ativo: true })
      .then(res => setProdutos(res.data.results || []))
      .finally(() => setLoading(false))
  }, [])

  // Busca estoque atual quando produto é selecionado
  useEffect(() => {
    if (!form.produto) { setProdutoAtual(null); return }
    produtosAPI.get(form.produto)
      .then(res => setProdutoAtual(res.data))
      .catch(() => setProdutoAtual(null))
  }, [form.produto])

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setErrors({})
    try {
      await movimentacoesAPI.create({
        produto: form.produto,
        tipo: form.tipo,
        quantidade: Number(form.quantidade),
        observacao: form.observacao,
      })
      navigate('/movimentacoes')
    } catch (err) {
      const data = err.response?.data || {}
      // Agrupa erros de campo e erros gerais
      setErrors(data)
    } finally {
      setSaving(false)
    }
  }

  const estoqueInfo = () => {
    if (!produtoAtual) return null
    const cor = produtoAtual.quantidade_atual === 0 ? 'danger'
      : produtoAtual.esta_abaixo_do_minimo ? 'warning' : 'info'
    return (
      <div className={`alert alert-${cor} d-flex justify-content-between align-items-center mb-4`}>
        <span><i className="bi bi-info-circle me-2"></i><strong>{produtoAtual.nome}</strong></span>
        <span>Estoque atual: <strong className="fs-5">{produtoAtual.quantidade_atual}</strong></span>
      </div>
    )
  }

  if (loading) return <Spinner />

  return (
    <>
      <div className="mb-4">
        <nav aria-label="breadcrumb">
          <ol className="breadcrumb small">
            <li className="breadcrumb-item"><Link to="/">Início</Link></li>
            <li className="breadcrumb-item"><Link to="/movimentacoes">Movimentações</Link></li>
            <li className="breadcrumb-item active">Nova</li>
          </ol>
        </nav>
      </div>

      <div className="row justify-content-center">
        <div className="col-lg-7">
          <div className="card shadow-sm">
            <div className="card-header bg-white py-3">
              <h5 className="mb-0 fw-bold">
                <i className="bi bi-arrow-left-right me-2 text-primary"></i>Registrar Movimentação
              </h5>
            </div>
            <div className="card-body">
              {estoqueInfo()}

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Produto <span className="text-danger">*</span></label>
                  <select className={`form-select ${errors.produto ? 'is-invalid' : ''}`}
                    value={form.produto} onChange={set('produto')} required>
                    <option value="">-- Selecione um produto --</option>
                    {produtos.map(p => (
                      <option key={p.id} value={p.id}>
                        {p.nome} (estoque: {p.quantidade_atual})
                      </option>
                    ))}
                  </select>
                  {errors.produto && <div className="invalid-feedback">{errors.produto.join(', ')}</div>}
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">Tipo <span className="text-danger">*</span></label>
                  <select className="form-select" value={form.tipo} onChange={set('tipo')}>
                    <option value="entrada">Entrada</option>
                    <option value="saida">Saída</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">Quantidade <span className="text-danger">*</span></label>
                  <input type="number" className={`form-control ${errors.quantidade ? 'is-invalid' : ''}`}
                    min="1" placeholder="Ex: 10"
                    value={form.quantidade} onChange={set('quantidade')} required />
                  {errors.quantidade && <div className="invalid-feedback">{errors.quantidade.join(', ')}</div>}
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">Observação</label>
                  <textarea className="form-control" rows={3}
                    placeholder="Nota fiscal, lote, motivo... (opcional)"
                    value={form.observacao} onChange={set('observacao')} />
                </div>

                {(errors.non_field_errors || errors.detail) && (
                  <div className="alert alert-danger">
                    {errors.non_field_errors?.join(', ') || errors.detail}
                  </div>
                )}

                <div className="d-flex gap-2 mt-4">
                  <button type="submit" className="btn btn-success" disabled={saving}>
                    {saving
                      ? <><span className="spinner-border spinner-border-sm me-1"></span>Registrando...</>
                      : <><i className="bi bi-check-lg me-1"></i>Registrar</>
                    }
                  </button>
                  <Link to="/movimentacoes" className="btn btn-outline-secondary">Cancelar</Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
