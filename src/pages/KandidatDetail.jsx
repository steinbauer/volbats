import { useParams } from 'react-router-dom'
import Hero from '../components/Hero'
import Nav from '../components/Nav'
import Prose from '../components/Prose'
import Meta from '../components/Meta'
import Rozcestnik from '../components/Rozcestnik'
import KandidatKarta from '../components/KandidatKarta'
import kandidati from '../data/kandidati.json'
import NotFound from './NotFound'

export default function KandidatDetail() {
  const { slug } = useParams()
  const kandidat = kandidati.find((k) => k.slug === slug)
  if (!kandidat) return <NotFound />

  return (
    <>
      <Meta
        title={`${kandidat.jmeno} | Volba pro město Trhové Sviny`}
        popis={kandidat.info}
      />
      <Hero />
      <Nav />

      <div className="container">
        <div className="row">
          <div className="col-12 col-sm-8 col-lg-9 content">
            <div className="kotva">
              <h1>{kandidat.jmeno}</h1>
            </div>
            <Prose html={kandidat.zivotopis} />
          </div>

          <div className="col-12 col-sm-4 col-lg-3">
            <KandidatKarta kandidat={{ ...kandidat, slug: null }} />
          </div>
        </div>
      </div>

      <br />
      <Rozcestnik />
      <br />
    </>
  )
}
