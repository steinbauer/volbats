import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Web běží na dvou místech s jiným kořenem:
//   GitHub Pages   https://steinbauer.github.io/volbats/   -> base '/volbats/'
//   lab (traefik)  https://main.volbats.kamil.lab.home/    -> base '/'
// Proto se base bere z proměnné a build pro Pages ji nastavuje ve workflow.
const base = process.env.VITE_BASE || '/'

export default defineConfig(({ isSsrBuild }) => ({
  base,
  plugins: [react()],
  css: {
    preprocessorOptions: {
      scss: {
        // Zbylá hlášení pocházejí ze samotného Bootstrapu 5.3, ne z naší
        // šablony — ta už je na @use převedená. Tlumíme je jmenovitě, aby
        // v logu neutopila varování, se kterými se dá něco dělat.
        // Až Bootstrap vyjde přepsaný na moduly, celý blok zmizí.
        silenceDeprecations: ['import', 'global-builtin', 'color-functions', 'if-function'],
      },
    },
  },
  build: {
    assetsDir: 'assets',
    rollupOptions: {
      output: isSsrBuild
        ? // SSR balík je jen meziprodukt pro prerender, hash by ho jen schoval
          { entryFileNames: 'entry-server.js' }
        : // V klientském buildu má každý soubor v názvu hash obsahu, takže po
          // nasazení nové verze prohlížeč nemá jak podstrčit starou — a nikdo
          // nemusí mačkat ctrl+F5.
          {
            entryFileNames: 'assets/[name]-[hash].js',
            chunkFileNames: 'assets/[name]-[hash].js',
            assetFileNames: 'assets/[name]-[hash][extname]',
          },
    },
  },
}))
