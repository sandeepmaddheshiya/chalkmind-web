# chalkmind.tech: Chalkmind landing site

Separate from the app repository. Deploy the `public/` folder.

Static HTML/CSS (no framework, no web fonts). About 12 KB compressed on first load.

| File | Purpose |
|---|---|
| `public/index.html` | Landing page (generated, see below) |
| `public/privacy.html`, `terms.html`, `support.html`, `404.html` | Policy and help pages (`/privacy` is required by Google Play) |
| `public/styles.css` | Shared styles (light + dark mode) |
| `public/favicon.svg`, `favicon-48.png`, `apple-touch-icon.png`, `og-image.png` | Icons and social preview image |
| `public/robots.txt`, `sitemap.xml` | Search engines |
| `Caddyfile` | VPS web server config (HTTPS, clean URLs, caching, security headers) |

## Edit

- Landing page text: edit `tools/index.template.html`, then run `python3 tools/build_index.py`
  (the chalkboard handwriting is generated from the app's own glyphs).
- Social image and touch icons: `python3 tools/generate_images.py` (needs Pillow).
  `tools/chalkmind_icon.py` is a copy of the app repo's brand mark; re-copy it if the logo changes.
- Other pages: edit the `.html` files directly.

## Preview locally

```sh
cd public && python3 -m http.server 8000   # open http://localhost:8000
```

## Deploy on the VPS

```sh
sudo apt install caddy                      # https://caddyserver.com/docs/install
sudo mkdir -p /var/www/chalkmind
rsync -av --delete public/ user@VPS:/var/www/chalkmind/
sudo cp Caddyfile /etc/caddy/Caddyfile && sudo systemctl reload caddy
```

DNS: point `chalkmind.tech` and `www.chalkmind.tech` (A/AAAA records) to the VPS
before reloading Caddy, so it can obtain the HTTPS certificate.

## Before launch

- When the app is live on Google Play, change the hero/footer call to action from
  "Join the beta" to the Play Store link: `https://play.google.com/store/apps/details?id=tech.chalkmind.app`.
- Have the privacy policy reviewed, and update it before adding sign-in, cloud backup
  or the AI server.
- Submit `https://chalkmind.tech/sitemap.xml` in Google Search Console.
