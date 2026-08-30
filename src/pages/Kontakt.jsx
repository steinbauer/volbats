import { useState } from 'react'
import Stranka from './Stranka'
import stranky from '../data/stranky.json'

const EMAIL = 'vera@korcak.cz'

/**
 * Kontaktní formulář.
 *
 * Původní web ho odesílal na server PolyWeb CMS s reCAPTCHOU. Statický web
 * žádný backend nemá, takže formulář poskládá zprávu a otevře ji v poštovním
 * klientovi. Až bude potřeba doručovat zprávy přímo, půjde to napojit na
 * externí službu (Formspree, Netlify Forms) — sem stačí vyměnit onSubmit.
 */
export default function Kontakt() {
  const [odeslano, setOdeslano] = useState(false)

  function odesli(e) {
    e.preventDefault()
    const f = new FormData(e.target)
    const telo = [
      `Jméno: ${f.get('jmeno')}`,
      `E-mail: ${f.get('email')}`,
      `Telefon: ${f.get('telefon')}`,
      '',
      f.get('vzkaz'),
    ].join('\n')
    window.location.href =
      `mailto:${EMAIL}?subject=${encodeURIComponent('Vzkaz z webu Volba pro město')}` +
      `&body=${encodeURIComponent(telo)}`
    setOdeslano(true)
  }

  return (
    <Stranka nadpis={stranky.kontakt.nadpis} html={stranky.kontakt.html}>
      <h2>Napište nám</h2>
      <form className="formular" onSubmit={odesli}>
        <div className="mb-3">
          <label className="form-label" htmlFor="jmeno">
            <span className="form_povinne">*</span> Vaše jméno a příjmení
          </label>
          <input className="form-control" id="jmeno" name="jmeno" required />
        </div>

        <div className="mb-3">
          <label className="form-label" htmlFor="email">
            <span className="form_povinne">*</span> Email pro odpověď
          </label>
          <input className="form-control" id="email" name="email" type="email" required />
        </div>

        <div className="mb-3">
          <label className="form-label" htmlFor="telefon">Telefon</label>
          <input className="form-control" id="telefon" name="telefon" type="tel" />
        </div>

        <div className="mb-3">
          <label className="form-label" htmlFor="vzkaz">
            <span className="form_povinne">*</span> Váš vzkaz
          </label>
          <textarea className="form-control" id="vzkaz" name="vzkaz" rows="6" required />
        </div>

        <button className="btn btn-warning btn-lg" type="submit">Odeslat</button>

        {odeslano && (
          <p className="mt-3">
            Zpráva se otevřela ve vašem poštovním programu. Pokud se nic nestalo,
            napište nám rovnou na <a href={`mailto:${EMAIL}`}>{EMAIL}</a>.
          </p>
        )}
      </form>
    </Stranka>
  )
}
