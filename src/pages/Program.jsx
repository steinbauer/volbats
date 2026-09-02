import Meta from '../components/Meta'
import Prose from '../components/Prose'
import ProgramBody from '../components/ProgramBody'
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
          <ProgramBody />
        </section>
      </div>
    </>
  )
}
