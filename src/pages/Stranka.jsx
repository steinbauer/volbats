import Nav from '../components/Nav'
import Prose from '../components/Prose'
import Meta from '../components/Meta'

/** Obyčejná textová stránka: nadpis a HTML obsah. */
export default function Stranka({ nadpis, html, popis, children }) {
  return (
    <>
      <Meta title={`${nadpis} | Volba pro město Trhové Sviny`} popis={popis} />
      <Nav />
      <div className="container">
        <div className="row">
          <div className="col-12 content">
            <div className="kotva">
              <h1>{nadpis}</h1>
            </div>
            {html && <Prose html={html} />}
            {children}
          </div>
        </div>
      </div>
      <br />
    </>
  )
}
