/**
 * Mapa jméno souboru -> URL s hashem, kterou vygeneroval Vite.
 *
 * Obrázky schválně nebydlí v public/, ale v src/obrazky/. Vite jim tak dá do
 * názvu hash obsahu, takže po nasazení nové verze prohlížeč nemá jak podstrčit
 * starý soubor — a nikdo nemusí mačkat ctrl+F5.
 */
const soubory = import.meta.glob('./obrazky/*', {
  eager: true,
  query: '?url',
  import: 'default',
})

const mapa = Object.fromEntries(
  Object.entries(soubory).map(([cesta, url]) => [cesta.replace('./obrazky/', ''), url]),
)

/**
 * Vrátí URL obrázku. Bere jméno souboru i cestu, jak ji zapsala extrakce
 * (`obrazky/foto.jpg`).
 */
export function obrazek(jmeno) {
  if (!jmeno) return jmeno
  return mapa[jmeno.replace(/^obrazky\//, '')] ?? jmeno
}

/**
 * Přepíše cesty v HTML přeneseném ze starého webu (`src="obrazky/foto.jpg"`)
 * na hashované URL.
 */
export function prepisObrazky(html) {
  return html.replace(/(src|href)="obrazky\/([^"]+)"/g, (cely, atribut, jmeno) => {
    const url = mapa[jmeno]  // jmeno je už bez prefixu obrazky/
    return url ? `${atribut}="${url}"` : cely
  })
}
