import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { categoriasAPI } from '../../api/endpoints'
import Spinner from '../../components/Spinner'

export default function CategoriaForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState({ nome: '', descricao: '' })
  const [loading, setLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (isEdit) {
      categoriasAPI.get(id)
        .then(res => setForm({ nome: res.data.nome, descricao: res.data.descricao || '' }))
        .finally(() => setLoading(false))
    }
  }, [id])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setErrors({})
    try {
      if (isEdit) await categoriasAPI.update(id, form)
      else await categoriasAPI.create(form)
      navigate('/categorias')
    } catch (err) {
      setErrors(err.response?.data || { nome: ['Erro ao salvar. Tente novamente.'] })
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <Spinner />

  return (
    <>
      <div className="mb-4">
        <nav aria-label="breadcrumb">
          <ol className="breadcrumb small">
            <li className="breadcrumb-item"><Link to="/">Início</Link></li>
            <li className="breadcrumb-item"><Link to="/categorias">Categorias</Link></li>
            <li className="breadcrumb-item active">{isEdit ? 'Editar' : 'Nova'}</li>
          </ol>
        </nav>
      </div>

      <div className="row justify-content-center">
        <div className="col-lg-6">
          <div className="card shadow-sm">
            <div className="card-header bg-white py-3">
              <h5 className="mb-0 fw-bold">
                <i className="bi bi-tag me-2 text-primary"></i>
                {isEdit ? `Editar: ${form.nome}` : 'Nova Categoria'}
              </h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Nome <span className="text-danger">*</span></label>
                  <input
                    type="text" className={`form-control ${errors.nome ? 'is-invalid' : ''}`}
                    placeholder="Nome da categoria"
                    value={form.nome}
                    onChange={e => setForm({ ...form, nome: e.target.value })}
                    required
                  />
                  {errors.nome && <div className="invalid-feedback">{errors.nome.join(', ')}</div>}
                </div>

                <div className="mb-4">
                  <label className="form-label fw-semibold">Descrição</label>
                  <textarea
                    className="form-control" rows={3} placeholder="Descrição opcional"
                    value={form.descricao}
                    onChange={e => setForm({ ...form, descricao: e.target.value })}
                  />
                </div>

                <div className="d-flex gap-2">
                  <button type="submit" className="btn btn-primary" disabled={saving}>
                    {saving
                      ? <><span className="spinner-border spinner-border-sm me-1"></span>Salvando...</>
                      : <><i className="bi bi-check-lg me-1"></i>{isEdit ? 'Salvar Alterações' : 'Salvar'}</>
                    }
                  </button>
                  <Link to="/categorias" className="btn btn-outline-secondary">Cancelar</Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
