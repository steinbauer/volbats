/**
 * Předgeneruje každou adresu do statického HTML.
 *
 * GitHub Pages neumí SPA fallback — kdyby se vracel jen jeden index.html,
 * přímý odkaz na /program/ by skončil na 404. Tímhle krokem vznikne pro
 * každou stránku skutečný soubor, takže adresy fungují napřímo, vyhledávače
 * vidí obsah bez spouštění JS a React se na hotové HTML jen napojí.
 */
import { readFile, writeFile, mkdir, rm } from 'node:fs/promises'
import { dirname, join } from 'node:path'

const KOREN = process.cwd()
const DIST = join(KOREN, 'dist')
const base = process.env.VITE_BASE || '/'
const zaklad = base.replace(/\/$/, '')

const sablona = await readFile(join(DIST, 'index.html'), 'utf-8')
const { render, vsechnyCesty, cestyBezIndexu } = await import(join(KOREN, 'dist-ssr/entry-server.js'))

// Náhrada se předává jako funkce, ne jako řetězec: v řetězci by `$&` nebo
// `$1` v titulku String.replace vyložil jako odkaz na shodu a text by se
// rozpadl.
function nahrad(html, vzor, nahrada) {
  return html.replace(vzor, () => nahrada)
}

/** Aby uvozovka nebo špičatá závorka v textu nerozbily značku. */
function escapuj(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/** Vloží do šablony titulek a popisek, které si stránka nastavila. */
function sHlavickou(html, meta) {
  if (meta.title) {
    html = nahrad(html, /<title>[\s\S]*?<\/title>/, `<title>${escapuj(meta.title)}</title>`)
  }
  if (meta.popis) {
    html = nahrad(
      html,
      /<meta\s+name="description"[\s\S]*?\/>/,
      `<meta name="description" content="${escapuj(meta.popis)}" />`,
    )
  }
  return html
}

for (const cesta of vsechnyCesty) {
  // StaticRouter porovnává location s basename, takže mu adresu předáváme
  // včetně prefixu (/volbats/program). Bez toho by na Pages nevykreslil nic.
  const { html, meta } = render(zaklad + cesta, zaklad)
  let stranka = sHlavickou(sablona, meta).replace('<!--app-html-->', html)

  // Staré adresy priorit ukazují celý program — do vyhledávačů ale patří
  // jen jednou, pod /program/. Z Reactu by se značka doplnila až po spuštění
  // JS, robot ji musí vidět rovnou v HTML.
  if (cestyBezIndexu.includes(cesta)) {
    stranka = stranka.replace(
      '</head>',
      '  <meta name="robots" content="noindex, nofollow" />\n  </head>',
    )
  }

  const soubor = cesta === '/'
    ? join(DIST, 'index.html')
    : join(DIST, cesta.slice(1), 'index.html')
  await mkdir(dirname(soubor), { recursive: true })
  await writeFile(soubor, stranka, 'utf-8')
}

// GitHub Pages servíruje 404.html u neznámých adres. Dáme mu tu samou
// aplikaci, aby i překlep skončil na naší stránce „nenalezeno" místo
// na obrazovce GitHubu.
const nenalezeno = render(`${zaklad}/404-neexistuje`, zaklad)
await writeFile(
  join(DIST, '404.html'),
  sHlavickou(sablona, nenalezeno.meta).replace('<!--app-html-->', nenalezeno.html),
  'utf-8',
)

// Jekyll by jinak přeskočil adresáře začínající podtržítkem
await writeFile(join(DIST, '.nojekyll'), '', 'utf-8')

// SSR build je jen meziprodukt, na Pages nemá co dělat
await rm(join(KOREN, 'dist-ssr'), { recursive: true, force: true })

console.log(`předgenerováno ${vsechnyCesty.length} stránek + 404`)
