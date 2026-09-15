// Adresy priorit z volebního programu 2022.
//
// Na volbats.cz stojí od roku 2022, mají je vyhledávače i odkazy odjinud.
// Program 2026 ale priority nemá — je to jedna stránka s tematickými
// sekcemi — takže na těchhle adresách je celý program. Předgenerují se,
// aby neodpověděly tvrdou 404, a prerender jim přidá noindex, ať se tentýž
// program neobjeví ve vyhledávačích dvacetkrát.
export const starePriority = [
  'pruhledne-a-ucelne-hospodareni',
  'ziskavani-dotaci',
  'dopravni-infrastruktura',
  'verejna-prostranstvi-a-zelen',
  'areal-stare-fary',
  'vodohospodarsky-majetek',
  'skolstvi',
  'podpora-rodin-s-detmi-volnocasove-aktivity',
  'podpora-senioru',
  'kultura',
  'sport',
  'zdravotnictvi',
  'socialni-sluzby',
  'cestovni-ruch',
  'bytova-politika',
  'spoluprace-s-firmami-a-podnikateli-ve-meste',
  'zapojeni-mesta-do-organizaci',
  'mistni-casti',
  'informacni-otevrenost',
]
