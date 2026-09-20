Static specimen site for Kureedo, served at https://kureedo.mkpo.li on Cloudflare Workers (static assets only, no worker script).
Deploy with `bunx wrangler deploy` from this directory; `public/fonts/` and `public/images/` are copies of `../fonts/` and `../docs/images/`, and `KureedoKanji-Subset.woff2` is `pyftsubset ../fonts/Kureedo-Regular.ttf --unicodes=U+5B50,U+4E95 --flavor=woff2 --layout-features=''` (the 子 and 井 of the comparison row).
The custom domain is declared in `wrangler.jsonc`, so the DNS record is created on deploy.

After a release: update the version, sizes and asset URLs in the download block of `public/index.html` (`gh release view --json tagName,assets`), copy the new webfont into `public/fonts/` (the "latest" alias) and into a new `public/vX.Y.Z/` folder, add `public/vX.Y.Z/kureedo.css` pinned to that folder, point `public/kureedo.css` and the snippets in the ウェブフォント配信 section at the new version, add the `/vX.Y.Z/*` block to `public/_headers`, and regenerate the glyph grids (one per Unicode block, cells Klee One lacks marked) with `../.venv/bin/python scripts/glyphs.py` (it rewrites the block between the `glyphs:start` and `glyphs:end` markers).
Old `public/vX.Y.Z/` folders stay: their URLs are immutable.

`public/_headers` sets CORS and cache headers: one year, immutable, for `/v*/`; one day for `/fonts/*` and `/kureedo.css`.
