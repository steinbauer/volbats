import { NavLink, useLocation } from 'react-router-dom'
import { menu } from '../data/navigace'

/**
 * Horní menu. Rozbalovací Priority nejedou na bootstrapím JS, ale na
 * :hover / :focus-within v CSS — díky tomu nepotřebujeme jQuery ani
 * bootstrap.bundle a menu funguje i před tím, než se stáhne JS.
 */
export default function Nav() {
  const { pathname } = useLocation()

  return (
    <div className="container-fluid background">
      <div className="container">
        <nav id="top_menu" aria-label="Hlavní menu">
              <ul className="navbar navbar-expand-lg">
                {menu.map((polozka) => {
                  const vPodmenu = polozka.podmenu?.some((p) => p.cesta === pathname)
                  return (
                    <li
                      key={polozka.cesta}
                      className={`nav-item${polozka.podmenu ? ' ma-podmenu' : ''}`}
                    >
                      <NavLink
                        to={polozka.cesta}
                        end={polozka.cesta === '/'}
                        className={({ isActive }) =>
                          `nav-link${isActive || vPodmenu ? ' active' : ''}`
                        }
                      >
                        <span>{polozka.popisek}</span>
                      </NavLink>

                      {polozka.podmenu && (
                        <ul className="podmenu">
                          {polozka.podmenu.map((pod) => (
                            <li key={pod.cesta} className="nav-item">
                              <NavLink
                                to={pod.cesta}
                                className={({ isActive }) =>
                                  `nav-link${isActive ? ' active' : ''}`
                                }
                              >
                                <span>{pod.popisek}</span>
                              </NavLink>
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  )
                })}
              </ul>
        </nav>
      </div>
    </div>
  )
}
