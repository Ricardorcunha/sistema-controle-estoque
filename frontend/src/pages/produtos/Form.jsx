import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { produtosAPI, categoriasAPI, fornecedoresAPI } from '../../api/endpoints'
import Spinner from '../../components/Spinner'

const INITIAL = { nome: '', categoria: '', fornecedor: '', preco: '', quantidade_minima: 0, ativo: true }

export default function ProdutoForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState(INITIAL)
  const [categorias, setCategorias] = useState([])
  const [fornecedores, setFornecedores] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    const fetchSelects = Promise.all([
      categoriasAPI.list({ page_size: 100 }),
      fornecedoresAPI.list({ page_size: 100, ativo: true }),
    ])
    const fetchProduto = isEdit ? produtosAPI.get(id) : Promise.resolve(null)

    Promise.all([fetchSelects, fetchProduto])
      .then(([[catRes, fornRes], prodRes]) => {
        setCategorias(catRes.data.results || [])
        setFornecedores(fornRes.data.results || [])
        if (prodRes) {
          const p = prodRes.data
          setForm({
            nome: p.nome,
            categoria: p.categoria?.id || p.categoria,
            fornecedor: p.fornecedor?.id || p.fornecedor,
            preco: p.preco,
            quantidade_minima: p.quantidade_minima,
            ativo: p.ativo,
          })
        }
      })
      .finally(() => setLoading(false))
  }, [id])

  const set = (field) => (e) =>
    setForm({ ...form, [field]: e.target.type === 'checkbox' ? e.target.checked : e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setErrors({})
    try {
      if (isEdit) await produtosAPI.update(id, form)
      else await produtosAPI.create(form)
      navigate('/produtos')
    } catch (err) {
      setErrors(err.response?.data || {})
    } finally {
      setSaving(false)
    }
  }

  const fieldError = (f) => errors[f]
    ? <div className="invalid-feedback d-block">{Array.isArray(errors[f]) ? errors[f].join(', ') : errors[f]}</div>
    : null

  if (loading) return <Spinner />

  return (
    <>
      <div className="mb-4">
        <nav aria-label="breadcrumb">
          <ol className="breadcrumb small">
            <li className="breadcrumb-item"><Link to="/">Início</Link></li>
            <li className="breadcrumb-item"><Link to="/produtos">Produtos</Link></li>
            <li className="breadcrumb-item active">{isEdit ? 'Editar' : 'Novo'}</li>
          </ol>
        </nav>
      </div>

      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-header bg-white py-3">
              <h5 className="mb-0 fw-bold">
                <i className="bi bi-box me-2 text-primary"></i>
                {isEdit ? `Editar: ${form.nome}` : 'Novo Produto'}
              </h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="row g-3">
                  <div className="col-12">
                    <label className="form-label fw-semibold">Nome <span className="text-danger">*</span></label>
                    <input type="text" className={`form-control ${errors.nome ? 'is-invalid' : ''}`}
                      placeholder="Nome do produto" value={form.nome} onChange={set('nome')} required />
                    {fieldError('nome')}
                  </div>

                  <div className="col-md-6">
                    <label className="form-label fw-semibold">Categoria <span className="text-danger">*</span></label>
                    <select className={`form-select ${errors.categoria ? 'is-invalid' : ''}`}
                      value={form.categoria} onChange={set('categoria')} required>
                      <option value="">-- Selecione --</option>
                      {categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                    </select>
                    {fieldError('categoria')}
                  </div>

                  <div className="col-md-6">
                    <label className="form-label fw-semibold">Fornecedor <span className="text-danger">*</span></label>
                    <select className={`form-select ${errors.fornecedor ? 'is-invalid' : ''}`}
                      value={form.fornecedor} onChange={set('fornecedor')} required>
                      <option value="">-- Selecione --</option>
                      {fornecedores.map(f => <option key={f.id} value={f.id}>{f.nome}</option>)}
                    </select>
                    {fieldError('fornecedor')}
                  </div>

                  <div className="col-md-6">
                    <label className="form-label fw-semibold">Preço (R$) <span className="text-danger">*</span></label>
                    <div className="input-group">
                      <span className="input-group-text">R$</span>
                      <input type="number" className={`form-control ${errors.preco ? 'is-invalid' : ''}`}
                        step="0.01" min="0" placeholder="0.00"
                        value={form.preco} onChange={set('preco')} required />
                    </div>
                    {fieldError('preco')}
                  </div>

                  <div className="col-md-6">
                    <label className="form-label fw-semibold">Quantidade Mínima</label>
                    <input type="number" className="form-control" min="0"
                      value={form.quantidade_minima} onChange={set('quantidade_minima')} />
                    <div className="form-text">Abaixo desse valor, o produto entra em alerta.</div>
                  </div>

                  <div className="col-12">
                    <div className="form-check">
                      <input className="form-check-input" type="checkbox" id="ativo"
                        checked={form.ativo} onChange={set('ativo')} />
                      <label className="form-check-label fw-semibold" htmlFor="ativo">Produto Ativo</label>
                    </div>
                  </div>
                </div>

                <div className="d-flex gap-2 mt-4">
                  <button type="submit" className="btn btn-primary" disabled={saving}>
                    {saving
                      ? <><span className="spinner-border spinner-border-sm me-1"></span>Salvando...</>
                      : <><i className="bi bi-check-lg me-1"></i>{isEdit ? 'Salvar Alterações' : 'Salvar'}</>
                    }
                  </button>
                  <Link to="/produtos" className="btn btn-outline-secondary">Cancelar</Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
