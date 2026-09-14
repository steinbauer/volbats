import { Link } from 'react-router-dom'
import { menu } from '../data/navigace'
import { web } from '../data/web'

export default function Footer() {
  // Patička dřív vypisovala priority; ty jsou teď schované spolu s programem,
  // tak v ní zbyly obyčejné odkazy z menu.
  const odkazy = menu.filter((p) => p.cesta !== '/')

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
              {odkazy.map((p) => (
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
