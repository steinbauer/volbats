import { Link } from 'react-router-dom'
import { stavProgramu } from '../data/program-stav'

/**
 * Pás „program se dolaďuje" na úvodní stránce. Stojí přesně tam, kde byly
 * body programu a dlaždice priorit — místo aby po nich zůstalo prázdné
 * místo, říká, proč tam zatím nejsou.
 */
export default function StavProgramu() {
  return (
    <section className="stav-programu">
      <div className="obal">
        <div className="stav-programu__stitek">{stavProgramu.stitek}</div>
        <h2>{stavProgramu.nadpis}</h2>

        {stavProgramu.odstavce.map((odstavec) => (
          <p className="stav-programu__text" key={odstavec}>
            {odstavec}
          </p>
        ))}

        <Link className="tlacitko tlacitko--zlute" to="/kandidati/">
          Zatím se podívejte na kandidátku
        </Link>
      </div>
    </section>
  )
}
