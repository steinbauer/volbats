import { NavLink } from 'react-router-dom'
import { menu } from '../data/navigace'

export default function Footer() {
  const priority = menu.find((p) => p.podmenu)?.podmenu ?? []

  return (
    <div className="background footer">
      <br />
      <div className="container">
        <div className="row">
          <div className="col-12 col-md-4">
            <h4>Volba pro město Trhové Sviny</h4>
            <div className="downmenu">
              <ul>
                {menu.map((polozka) => (
                  <li key={polozka.cesta}>
                    <NavLink to={polozka.cesta} end={polozka.cesta === '/'}>
                      <span>{polozka.popisek}</span>
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="col-12 col-md-8">
            <h4>Priority</h4>
            <div className="downmenu downmenu-inline">
              <ul>
                {priority.map((polozka) => (
                  <li key={polozka.cesta}>
                    <NavLink to={polozka.cesta}>
                      <span>{polozka.popisek}</span>
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="row">
          <div className="col-12 text-end text-small">
            © 2022 - Volba pro město Trhové Sviny
          </div>
        </div>
      </div>
      <br />
    </div>
  )
}
