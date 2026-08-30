import { Link } from 'react-router-dom'

/** Dva boxy pod obsahem — dřív .jumbotron, ten v Bootstrapu 5 už není. */
export default function Rozcestnik() {
  const boxy = [
    { cesta: '/program', nadpis: 'Náš program', tlacitko: 'Zobrazit náš program' },
    { cesta: '/kandidati', nadpis: 'Naši kandidáti', tlacitko: 'Zobrazit naše kandidáty' },
  ]

  return (
    <div className="container">
      <div className="row">
        {boxy.map((box) => (
          <div className="col-12 col-md-6" key={box.cesta}>
            <Link className="box text-center box-anchor" to={box.cesta}>
              <h2>{box.nadpis}</h2>
              <p className="lead">
                <span className="btn btn-warning btn-lg">{box.tlacitko}</span>
              </p>
            </Link>
          </div>
        ))}
      </div>
    </div>
  )
}
