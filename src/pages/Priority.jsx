import { Link } from 'react-router-dom'
import Meta from '../components/Meta'
import Prose from '../components/Prose'
import priority from '../data/priority.json'
import stranky from '../data/stranky.json'

export default function Priority() {
  return (
    <>
      <Meta title="Priority | Volba pro město Trhové Sviny" />
      <div className="obal">
        <section className="sekce">
          <h1>{stranky.priority.nadpis}</h1>
          <div className="text mt-4 mb-5">
            <Prose html={stranky.priority.html} />
          </div>

          <div className="dlazdice-priorit dlazdice-priorit--svetle">
            {priority.map((p, i) => (
              <Link to={`/priority/${p.slug}/`} key={p.slug}>
                <span className="dlazdice-priorit__cislo">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span className="dlazdice-priorit__nazev">{p.nadpis}</span>
                <span className="dlazdice-priorit__vic">Číst prioritu →</span>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </>
  )
}
