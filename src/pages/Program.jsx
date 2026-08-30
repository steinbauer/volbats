import Stranka from './Stranka'
import Prose from '../components/Prose'
import stranky from '../data/stranky.json'
import tabulka from '../data/program-tabulka.json'

export default function Program() {
  return (
    <Stranka nadpis={stranky.program.nadpis} html={stranky.program.html}>
      {tabulka.map((radek, i) => (
        <div className="row border m-3" key={i}>
          {radek.map((sloupec, j) => (
            <div className="col-12 col-sm-6" key={j}>
              <h2>{sloupec.nadpis}</h2>
              <Prose html={sloupec.html} />
            </div>
          ))}
        </div>
      ))}
    </Stranka>
  )
}
