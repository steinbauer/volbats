import { Link } from 'react-router-dom'
import Nav from '../components/Nav'
import Meta from '../components/Meta'

export default function NotFound() {
  return (
    <>
      <Meta title="Stránka nenalezena | Volba pro město Trhové Sviny" />
      <Nav />
      <div className="container">
        <div className="row">
          <div className="col-12 content">
            <div className="kotva">
              <h1>Stránka nenalezena</h1>
            </div>
            <p>Taková stránka tu není. Zkuste to z <Link to="/">úvodní stránky</Link>.</p>
          </div>
        </div>
      </div>
      <br />
    </>
  )
}
