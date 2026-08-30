import { Link } from 'react-router-dom'
import Meta from '../components/Meta'

export default function NotFound() {
  return (
    <>
      <Meta title="Stránka nenalezena | Volba pro město Trhové Sviny" />
      <div className="obal">
        <section className="sekce">
          <h1>Stránka nenalezena</h1>
          <p className="uvod__perex mt-4">
            Taková stránka tu není. Zkuste to z <Link to="/">úvodní stránky</Link>.
          </p>
        </section>
      </div>
    </>
  )
}
