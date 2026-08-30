import Meta from '../components/Meta'
import Prose from '../components/Prose'
import Bilance from '../components/Bilance'
import stranky from '../data/stranky.json'

export default function Program() {
  return (
    <>
      <Meta title="Program | Volba pro město Trhové Sviny" />
      <div className="obal">
        <section className="sekce">
          <h1>{stranky.program.nadpis}</h1>
          <div className="text mt-4 mb-5">
            <Prose html={stranky.program.html} />
          </div>
          <Bilance />
        </section>
      </div>
    </>
  )
}
