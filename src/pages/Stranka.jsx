import Meta from '../components/Meta'
import Prose from '../components/Prose'

/** Obyčejná textová stránka: nadtitulek, nadpis a obsah. */
export default function Stranka({ nadpis, html, perex, popis, children }) {
  return (
    <>
      <Meta title={`${nadpis} | Volba pro město Trhové Sviny`} popis={popis} />
      <div className="obal">
        <section className="sekce">
          <h1>{nadpis}</h1>
          {perex && <p className="uvod__perex mt-4">{perex}</p>}
          <div className="text mt-4">
            {html && <Prose html={html} />}
            {children}
          </div>
        </section>
      </div>
    </>
  )
}
