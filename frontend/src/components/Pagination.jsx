/**
 * Pagination — componente de paginação reutilizável.
 *
 * Props:
 *   count      — total de itens
 *   pageSize   — itens por página (padrão 20)
 *   page       — página atual
 *   onPageChange(newPage) — callback ao mudar página
 */
export default function Pagination({ count, pageSize = 20, page, onPageChange }) {
  const totalPages = Math.ceil(count / pageSize)
  if (totalPages <= 1) return null

  return (
    <nav>
      <ul className="pagination pagination-sm mb-0 justify-content-center">
        <li className={`page-item ${page === 1 ? 'disabled' : ''}`}>
          <button className="page-link" onClick={() => onPageChange(page - 1)}>«</button>
        </li>
        <li className="page-item disabled">
          <span className="page-link">{page} / {totalPages}</span>
        </li>
        <li className={`page-item ${page === totalPages ? 'disabled' : ''}`}>
          <button className="page-link" onClick={() => onPageChange(page + 1)}>»</button>
        </li>
      </ul>
    </nav>
  )
}
