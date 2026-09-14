import kandidati from './kandidati.json'

/**
 * Vlastní stránku má ten, komu dorazil medailonek. Ostatní zůstávají na
 * dlaždicích bez odkazu — kdyby stránku měli, byly by na ní jen údaje
 * z kandidátní listiny. Text v datech je tedy zároveň rozhodnutí, že
 * medailonek jde na web.
 */
export function maStranku(kandidat) {
  return Boolean(kandidat.zivotopis)
}

/** Odkaz na medailonek, nebo null, když ho kandidát nemá. */
export function odkazNaMedailonek(kandidat) {
  return maStranku(kandidat) ? `/kandidati/${kandidat.slug}/` : null
}

export { kandidati }
