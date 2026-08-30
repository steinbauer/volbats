import { useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { menu } from '../data/navigace'
import { web } from '../data/web'
import Znak from './Znak'

export default function Header() {
  const [otevreno, setOtevreno] = useState(false)
  const { pathname } = useLocation()

  return (
    <header className="hlavicka">
      <div className="obal">
        <Link className="logo" to="/" onClick={() => setOtevreno(false)}>
          <Znak className="logo__znak" aria-hidden="true" />
          <span>
            <span className="logo__nazev d-block">{web.nazev}</span>
            <span className="logo__mesto d-block">{web.mesto}</span>
          </span>
        </Link>

        <button
          className="menu-prepinac"
          type="button"
          aria-expanded={otevreno}
          onClick={() => setOtevreno((o) => !o)}
        >
          {otevreno ? 'Zavřít' : 'Menu'}
        </button>

        {/* Na širokém displeji je menu vidět vždy; v mobilním zalomení ho
            odkrývá třída menu--otevrene. Atribut hidden použít nejde —
            Bootstrap má [hidden] { display: none !important }, takže by
            menu zmizelo i na desktopu. */}
        <div className="hlavicka__vpravo">
        <ul className={`menu${otevreno ? ' menu--otevrene' : ''}`}>
          {menu.map((polozka) => {
            const vPodmenu = polozka.podmenu?.some((p) => p.cesta === pathname)
            return (
              <li key={polozka.cesta} className={polozka.podmenu ? 'ma-podmenu' : undefined}>
                <NavLink
                  to={polozka.cesta}
                  end={polozka.cesta === '/'}
                  onClick={() => setOtevreno(false)}
                  className={({ isActive }) => (isActive || vPodmenu ? 'active' : undefined)}
                >
                  {polozka.popisek}
                </NavLink>

                {polozka.podmenu && (
                  <ul className="podmenu">
                    {polozka.podmenu.map((pod) => (
                      <li key={pod.cesta}>
                        <NavLink
                          to={pod.cesta}
                          onClick={() => setOtevreno(false)}
                          className={({ isActive }) => (isActive ? 'active' : undefined)}
                        >
                          {pod.popisek}
                        </NavLink>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            )
          })}
        </ul>
        <span className="termin">{web.termin}</span>
        </div>
      </div>
    </header>
  )
}
