import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { fornecedoresAPI } from '../../api/endpoints'
import Spinner from '../../components/Spinner'

const INITIAL = { nome: '', cnpj: '', email: '', telefone: '', ativo: true }

export default function FornecedorForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState(INITIAL)
  const [loading, setLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (isEdit) {
      fornecedoresAPI.get(id)
        .then(res => setForm({
          nome: res.data.nome || '',
          cnpj: res.data.cnpj || '',
          email: res.data.email || '',
          telefone: res.data.telefone || '',
          ativo: res.data.ativo,
        }))
        .finally(() => setLoading(false))
    }
  }, [id])

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.type === 'checkbox' ? e.target.checked : e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setErrors({})
    try {
      if (isEdit) await fornecedoresAPI.update(id, form)
      else await fornecedoresAPI.create(form)
      navigate('/fornecedores')
    } catch (err) {
      setErrors(err.response?.data || {})
    } finally {
      setSaving(false)
    }
  }

  const fieldError = (f) => errors[f] ? (
    <div className="invalid-feedback d-block">{errors[f].join(', ')}</div>
  ) : null

  if (loading) return <Spinner />

  return (
    <>
      <div className="mb-4">
        <nav aria-label="breadcrumb">
          <ol className="breadcrumb small">
            <li className="breadcrumb-item"><Link to="/">Início</Link></li>
            <li className="breadcrumb-item"><Link to="/fornecedores">Fornecedores</Link></li>
            <li className="breadcrumb-item active">{isEdit ? 'Editar' : 'Novo'}</li>
          </ol>
        </nav>
      </div>

      <div className="row justify-content-center">
        <div className="col-lg-7">
          <div className="card shadow-sm">
            <div className="card-header bg-white py-3">
              <h5 className="mb-0 fw-bold">
                <i className="bi bi-truck me-2 text-primary"></i>
                {isEdit ? `Editar: ${form.nome}` : 'Novo Fornecedor'}
              </h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="row g-3">
                  <div className="col-12">
                    <label className="form-label fw-semibold">Nome / Razão Social <span className="text-danger">*</span></label>
                    <input type="text" className={`form-control ${errors.nome ? 'is-invalid' : ''}`}
                      placeholder="Nome do fornecedor" value={form.nome} onChange={set('nome')} required />
                    {fieldError('nome')}
                  </div>

                  <div className="col-md-6">
                    <label className="form-label fw-semibold">CNPJ</label>
                    <input type="text" className={`form-control ${errors.cnpj ? 'is-invalid' : ''}`}
                      placeholder="00.000.000/0000-00" value={form.cnpj} onChange={set('cnpj')} />
                    {fieldError('cnpj')}
                  </div>

                  <div className="col-md-6">
                    <label className="form-label fw-semibold">Telefone</label>
                    <input type="text" className="form-control"
                      placeholder="(11) 00000-0000" value={form.telefone} onChange={set('telefone')} />
                  </div>

                  <div className="col-12">
                    <label className="form-label fw-semibold">Email</label>
                    <input type="email" className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                      placeholder="contato@empresa.com" value={form.email} onChange={set('email')} />
                    {fieldError('email')}
                  </div>

                  <div className="col-12">
                    <div className="form-check">
                      <input className="form-check-input" type="checkbox" id="ativo"
                        checked={form.ativo} onChange={set('ativo')} />
                      <label className="form-check-label fw-semibold" htmlFor="ativo">Fornecedor Ativo</label>
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
                  <Link to="/fornecedores" className="btn btn-outline-secondary">Cancelar</Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
