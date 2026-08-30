import priority from './priority.json'

// Hlavní menu. Priority se doplňují z dat, aby se seznam držel na jednom místě.
export const menu = [
  { cesta: '/', popisek: 'Volba pro město' },
  {
    cesta: '/priority/',
    popisek: 'Priority',
    podmenu: priority.map((p) => ({
      cesta: `/priority/${p.slug}/`,
      popisek: p.nadpis,
    })),
  },
  { cesta: '/program/', popisek: 'Program' },
  { cesta: '/kandidati/', popisek: 'Kandidáti' },
  { cesta: '/kontakt/', popisek: 'Kontakt' },
]
