Static specimen site for Kureedo, served at https://kureedo.mkpo.li on Cloudflare Workers (static assets only, no worker script).
Deploy with `bunx wrangler deploy` from this directory; `public/fonts/` and `public/images/` are copies of `../fonts/` and `../docs/images/`, and `KureedoKanji-Subset.woff2` is `pyftsubset ../fonts/Kureedo-Regular.ttf --unicodes=U+5B50,U+4E95 --flavor=woff2 --layout-features=''` (the 子 and 井 of the comparison row).
The custom domain is declared in `wrangler.jsonc`, so the DNS record is created on deploy.

After a release: update the version, sizes and asset URLs in the download block of `public/index.html` (`gh release view --json tagName,assets`), copy the new webfont into `public/fonts/`, and regenerate the glyph grid from its cmap with `../.venv/bin/python scripts/glyphs.py` (it rewrites the block between the `glyphs:start` and `glyphs:end` markers).
