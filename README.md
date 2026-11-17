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

Every page except the home page is generated from `content/`:

| Folder | Pages |
|---|---|
| `content/*.html` | Feature pages (`/handwritten-math-solver`, `/check-my-math`, …), legal pages, `/thanks` |
| `content/for/` | Audience pages: teachers, students, tutors, parents |
| `content/subjects/` | Algebra, geometry |
| `content/compare/` | Honest comparisons (dated; re-check competitors' sites before editing) |
| `content/guides/` | Long guides; `/guides` lists them automatically |
| `content/_visuals/` | Hero illustrations (`{{HW|2x = 4|x|y|size|class}}` draws handwriting) |

Each file starts with a JSON `<!--meta … -->` block (path, title, description, h1, lede, FAQ, related pages,
`role` for the sign-up form), followed by the page HTML. `<!--cta-->` inside a guide inserts a call-to-action box.

```sh
python3 tools/build_site.py     # builds every page, the home page and sitemap.xml
```

- Home page text: `tools/index.template.html` (built by the same command).
- Shared header, footer and early-access form: `tools/site_parts.py`.
- **When the app is on Google Play:** set `PLAY_URL` in `tools/site_parts.py` and rebuild. Every
  “Get early access” button and form becomes a Google Play link.
- Social image and touch icons: `python3 tools/generate_images.py` (needs Pillow).

### Sign-ups and page views

The early-access form posts to `https://api.chalkmind.tech/v1/waitlist`, and `public/site.js` counts page
views at `/v1/pv` (path only, no cookies, respects Do Not Track). Results are in the admin console under
**Website & sign-ups**: views, sign-ups and conversion rate per page, referrers and `utm_source` campaigns,
and a CSV export of the list. Add `?utm_source=reddit&utm_campaign=launch` to links you share to see which
posts bring sign-ups.

## Preview locally

```sh
python3 tools/serve.py   # open http://localhost:8000 (same clean URLs as the live site)
```

## Deploy on the VPS (nginx, alongside other sites)

The VPS already runs other sites behind nginx, so this site is just one more
nginx server block serving static files. No pm2/Node process is needed, and
other sites are not touched.

```sh
# 1. Files (first time)
sudo git clone https://github.com/sandeepmaddheshiya/chalkmind-web.git /var/www/chalkmind-web

# 2. nginx site
sudo cp /var/www/chalkmind-web/deploy/nginx-chalkmind.tech.conf /etc/nginx/sites-available/chalkmind.tech
sudo ln -s /etc/nginx/sites-available/chalkmind.tech /etc/nginx/sites-enabled/chalkmind.tech
sudo nginx -t && sudo systemctl reload nginx     # reload = no downtime for other sites

# 3. HTTPS (after DNS A records point to the VPS)
sudo certbot --nginx -d chalkmind.tech -d www.chalkmind.tech
```

Update the live site later:

```sh
cd /var/www/chalkmind-web && sudo git pull
```

(`Caddyfile` is an alternative for a server that runs Caddy instead of nginx.)

## Before launch

- When the app is live on Google Play, set `PLAY_URL = "https://play.google.com/store/apps/details?id=tech.chalkmind.app"`
  in `tools/site_parts.py` and run `python3 tools/build_site.py`.
- Submit `https://chalkmind.tech/sitemap.xml` in Google Search Console and Bing Webmaster Tools.
- Have the privacy policy reviewed, and update it before adding sign-in, cloud backup
  or the AI server.
- Submit `https://chalkmind.tech/sitemap.xml` in Google Search Console.
