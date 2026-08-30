import { Link } from 'react-router-dom'
import { obrazek } from '../obrazky'

export default function Header() {
  return (
    <div className="container">
      <div className="row header">
        <div className="col-12 text-center">
          <Link to="/">
            <img
              src={obrazek('volbats.png')}
              className="img-fluid"
              alt="Volba pro město Trhové Sviny"
            />
          </Link>
        </div>
      </div>
    </div>
  )
}
