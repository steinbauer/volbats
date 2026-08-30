import Nav from '../components/Nav'
import Meta from '../components/Meta'
import KandidatKarta from '../components/KandidatKarta'
import kandidati from '../data/kandidati.json'
import stranky from '../data/stranky.json'
import Prose from '../components/Prose'

export default function Kandidati() {
  return (
    <>
      <Meta title="Kandidáti | Volba pro město Trhové Sviny" />
      <Nav />
      <div className="container">
        <div className="row">
          <div className="col-12 content">
            <div className="kotva">
              <h1>Naši kandidáti</h1>
            </div>
            {stranky.kandidati?.html && <Prose html={stranky.kandidati.html} />}

            <div className="row">
              {kandidati.map((k) => (
                <div className="col-12 col-sm-6 col-lg-3" key={k.cislo ?? k.jmeno}>
                  <KandidatKarta kandidat={k} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <br />
    </>
  )
}
