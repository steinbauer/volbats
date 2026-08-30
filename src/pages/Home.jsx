import Hero from '../components/Hero'
import Rozcestnik from '../components/Rozcestnik'
import Prose from '../components/Prose'
import Galerie from '../components/Galerie'
import Nav from '../components/Nav'
import stranky from '../data/stranky.json'
import Meta from '../components/Meta'

export default function Home() {
  const { nadpis, html } = stranky.home

  return (
    <>
      <Meta title="Volba pro město Trhové Sviny" />
      <Hero />
      <Nav />

      <div className="container">
        <div className="row">
          <div className="col-12 content">
            <div className="kotva">
              <h1>{nadpis}</h1>
            </div>
            <Prose html={html} />
            <Galerie />
          </div>
        </div>
      </div>

      <br />
      <Rozcestnik />
      <br />
    </>
  )
}
