import kandidati from './kandidati.json'

/**
 * Dokud nejsou medailonky napsané pro všechny, má vlastní stránku jen prvních
 * pár lidí na kandidátce. Ostatní zůstávají na dlaždicích bez odkazu.
 * Až texty dorazí, stačí zvednout tuhle hodnotu.
 */
export const MEDAILONKY_DO = 10

/** Má kandidát vlastní stránku? */
export function maStranku(kandidat) {
  return kandidat.cislo <= MEDAILONKY_DO
}

/** Odkaz na medailonek, nebo null, když ho kandidát nemá. */
export function odkazNaMedailonek(kandidat) {
  return maStranku(kandidat) ? `/kandidati/${kandidat.slug}/` : null
}

export { kandidati }
