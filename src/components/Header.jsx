import { useEffect, useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { menu } from '../data/navigace'
import { web } from '../data/web'
import Logo from './Logo'
import Znak from './Znak'

// Meze pro scvrknutí loga. Dvě, ne jedna: kolem jediné hranice logo poskakuje
// sem a tam, protože i malá změna výšky obsahu posune scrollY zpátky přes ni.
const SCVRKNOUT = 110
const ROZBALIT = 40

export default function Header() {
  const [otevreno, setOtevreno] = useState(false)
  const [sjete, setSjete] = useState(false)
  const { pathname } = useLocation()
  const naUvodu = pathname === '/'

  /**
   * Na úvodní stránce začíná logo velké a přesahuje do společné fotky;
   * jakmile návštěvník odroluje, přejde do řádkové podoby v liště. Je to
   * jediný trik, který funguje stejně na širokém displeji i na mobilu —
   * srdce se nikde neobjeví dvakrát a na mobilu nezabere půl obrazovky.
   */
  useEffect(() => {
    if (!naUvodu) {
      setSjete(false)
      return
    }
    const zjisti = () =>
      setSjete((bylo) => {
        if (window.scrollY > SCVRKNOUT) return true
        if (window.scrollY < ROZBALIT) return false
        return bylo
      })
    zjisti()
    window.addEventListener('scroll', zjisti, { passive: true })
    return () => window.removeEventListener('scroll', zjisti)
  }, [naUvodu])

  const velke = naUvodu && !sjete

  return (
    <header className={`hlavicka${velke ? ' hlavicka--velke-logo' : ''}`}>
      <div className="obal">
        <Link className="logo" to="/" onClick={() => setOtevreno(false)}>
          {/* Obě podoby loga jsou v DOM pořád a přepínají se průhledností,
              aby mezi nimi šlo plynule přejít. Ta schovaná je vyřazená
              z přístupnosti, ať čtečka nepředčítá název dvakrát. */}
          <span className="logo__velke" aria-hidden={!velke}>
            <Logo />
          </span>
          <span className="logo__radkove" aria-hidden={velke}>
            <Znak className="logo__znak" barva="#c23a22" aria-hidden="true" />
            <span>
              <span className="logo__nazev d-block">{web.nazev}</span>
              <span className="logo__mesto d-block">{web.mesto}</span>
              <span className="logo__claim d-block">{web.claim}</span>
            </span>
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
