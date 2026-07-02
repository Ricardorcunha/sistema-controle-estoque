import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const isAdmin = user?.perfil === 'admin' || user?.is_superuser

  return (
    <div>
      {/* ── Sidebar ── */}
      <nav id="sidebar">
        <div className="sidebar-brand">
          <div className="d-flex align-items-center gap-2">
            <i className="bi bi-box-seam text-white fs-5"></i>
            <span className="text-white fw-bold">Estoque Pro</span>
          </div>
          <div className="text-white-50 small mt-1">Sistema de Controle</div>
        </div>

        <div className="py-2">
          <div className="sidebar-section">Principal</div>
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <i className="bi bi-speedometer2 me-2"></i> Dashboard
          </NavLink>

          <div className="sidebar-section">Estoque</div>
          <NavLink to="/produtos" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <i className="bi bi-box-seam me-2"></i> Produtos
          </NavLink>
          <NavLink to="/movimentacoes" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <i className="bi bi-arrow-left-right me-2"></i> Movimentações
          </NavLink>

          {isAdmin && (
            <>
              <div className="sidebar-section">Cadastros</div>
              <NavLink to="/categorias" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                <i className="bi bi-tags me-2"></i> Categorias
              </NavLink>
              <NavLink to="/fornecedores" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                <i className="bi bi-truck me-2"></i> Fornecedores
              </NavLink>
            </>
          )}

          <div className="sidebar-section">Sistema</div>
          <a href="/api/docs/" target="_blank" className="nav-link">
            <i className="bi bi-code-slash me-2"></i> API Docs
          </a>
          <a href="/admin/" target="_blank" className="nav-link">
            <i className="bi bi-gear me-2"></i> Admin Django
          </a>
        </div>
      </nav>

      {/* ── Main ── */}
      <div id="main-content">
        {/* Topbar */}
        <div id="topbar">
          <div className="d-flex align-items-center gap-3">
            <button
              className="btn btn-sm btn-outline-secondary d-md-none"
              onClick={() => document.getElementById('sidebar').classList.toggle('show')}
            >
              <i className="bi bi-list"></i>
            </button>
          </div>
          <div className="dropdown">
            <button className="btn btn-sm d-flex align-items-center gap-2" data-bs-toggle="dropdown">
              <div
                className="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center"
                style={{ width: 32, height: 32, fontSize: '0.8rem' }}
              >
                {(user?.username?.[0] || 'U').toUpperCase()}
              </div>
              <span className="small fw-semibold d-none d-md-inline">{user?.username}</span>
              <i className="bi bi-chevron-down small"></i>
            </button>
            <ul className="dropdown-menu dropdown-menu-end">
              <li><span className="dropdown-item-text text-muted small">{user?.email || user?.username}</span></li>
              <li><hr className="dropdown-divider" /></li>
              <li>
                <button className="dropdown-item text-danger" onClick={logout}>
                  <i className="bi bi-box-arrow-right me-2"></i>Sair
                </button>
              </li>
            </ul>
          </div>
        </div>

        {/* Conteúdo das páginas */}
        <div id="page-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
