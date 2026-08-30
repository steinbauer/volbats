import { Link } from 'react-router-dom'
import { menu } from '../data/navigace'
import { web } from '../data/web'

export default function Footer() {
  const priority = menu.find((p) => p.podmenu)?.podmenu ?? []

  return (
    <>
      <div className="pruh-paticky" />
      <footer className="paticka">
        <div className="obal">
          <div>
            <div className="paticka__nazev">
              {web.nazev} {web.mesto}
            </div>
            <div>{web.claim}</div>
            <div className="mt-3">
              <a href={`mailto:${web.email}`}>{web.email}</a>
            </div>
          </div>

          <div>
            <ul className="paticka__odkazy">
              {priority.map((p) => (
                <li key={p.cesta}>
                  <Link to={p.cesta}>{p.popisek}</Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            © {web.rok} · {web.nazev}, politické hnutí
          </div>
        </div>
      </footer>
    </>
  )
}
