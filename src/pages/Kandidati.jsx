import Meta from '../components/Meta'
import Prose from '../components/Prose'
import KandidatKarta from '../components/KandidatKarta'
import kandidati from '../data/kandidati.json'
import stranky from '../data/stranky.json'

const SIZES =
  '(min-width: 1200px) 310px, (min-width: 992px) 22vw, (min-width: 768px) 30vw, 45vw'

export default function Kandidati() {
  return (
    <>
      <Meta title="Kandidáti | Volba pro město Trhové Sviny" />
      <div className="obal">
        <section className="sekce">
          <h1>{stranky.kandidati.nadpis}</h1>
          <div className="text mt-4 mb-5">
            <Prose html={stranky.kandidati.html} />
          </div>

          <div className="mrizka-kandidatu">
            {kandidati.map((k) => (
              <KandidatKarta kandidat={k} sizes={SIZES} key={k.cislo} />
            ))}
          </div>
        </section>
      </div>
    </>
  )
}
