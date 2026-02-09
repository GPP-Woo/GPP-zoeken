import * as esbuild from 'esbuild';
import {sassPlugin} from 'esbuild-sass-plugin';

await esbuild.build({
  entryPoints: [
    'src/woo_search/scss/screen.scss',
    'src/woo_search/scss/admin/admin_overrides.scss',
  ],
  bundle: true,
  minify: true,
  sourcemap: true,
  outdir: 'src/woo_search/static/bundles/',
  plugins: [sassPlugin({embedded: true})],
  external: ['*.svg', '*.png', '*.woff2', '*.ttf'],
})
