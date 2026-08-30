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
const { render, vsechnyCesty } = await import(join(KOREN, 'dist-ssr/entry-server.js'))

for (const cesta of vsechnyCesty) {
  // StaticRouter porovnává location s basename, takže mu adresu předáváme
  // včetně prefixu (/volbats/program). Bez toho by na Pages nevykreslil nic.
  const html = render(zaklad + cesta, zaklad)
  const stranka = sablona.replace('<!--app-html-->', html)
  const soubor = cesta === '/'
    ? join(DIST, 'index.html')
    : join(DIST, cesta.slice(1), 'index.html')
  await mkdir(dirname(soubor), { recursive: true })
  await writeFile(soubor, stranka, 'utf-8')
}

// GitHub Pages servíruje 404.html u neznámých adres. Dáme mu tu samou
// aplikaci, aby i překlep skončil na naší stránce „nenalezeno" místo
// na obrazovce GitHubu.
await writeFile(
  join(DIST, '404.html'),
  sablona.replace('<!--app-html-->', render(`${zaklad}/404-neexistuje`, zaklad)),
  'utf-8',
)

// Jekyll by jinak přeskočil adresáře začínající podtržítkem
await writeFile(join(DIST, '.nojekyll'), '', 'utf-8')

// SSR build je jen meziprodukt, na Pages nemá co dělat
await rm(join(KOREN, 'dist-ssr'), { recursive: true, force: true })

console.log(`předgenerováno ${vsechnyCesty.length} stránek + 404`)
