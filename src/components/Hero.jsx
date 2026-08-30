import { obrazek } from '../obrazky'

export default function Hero() {
  return (
    <div className="container-fluid hp">
      <div className="row">
        <div className="list">
          <img
            src={obrazek('kandidati-volbats.jpg')}
            className="img-fluid"
            alt="Kandidáti Volba pro město Trhové Sviny"
          />
        </div>
      </div>
    </div>
  )
}
