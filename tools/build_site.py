"""Builds every content page, the sitemap and the home page.

Content lives in content/**/*.html. Each file starts with a JSON block:

    <!--meta
    {"path": "/for/teachers", "type": "landing", "title": "...", "description": "...",
     "h1": "...", "lede": "...", "label": "Teachers", "faq": [["Q", "A"]], "related": ["/..."]}
    -->

followed by the page body (HTML). Types: landing, guide, hub, doc, thanks.
Run from the repo root:  python3 tools/build_site.py
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import site_parts as sp

ROOT = sp.ROOT
PUBLIC = os.path.join(ROOT, 'public')
TODAY = datetime.date.today().isoformat()
esc = sp.esc


def load_pages():
    pages = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'content', '**', '*.html'), recursive=True)):
        if os.sep + '_visuals' + os.sep in f:
            continue
        raw = open(f, encoding='utf-8').read()
        m = re.match(r'\s*<!--meta\s*(\{.*?\})\s*-->\s*', raw, re.S)
        if not m:
            raise SystemExit(f'{f}: missing <!--meta {{...}} --> header')
        meta = json.loads(m.group(1))
        meta['body'] = raw[m.end():]
        meta.setdefault('type', 'landing')
        meta.setdefault('updated', TODAY)
        meta['_file'] = os.path.relpath(f, ROOT)
        pages.append(meta)
    paths = [p['path'] for p in pages]
    dupes = {p for p in paths if paths.count(p) > 1}
    if dupes:
        raise SystemExit(f'duplicate paths: {dupes}')
    return pages


def jsonld(obj):
    return '\n  <script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


def breadcrumbs(crumbs):
    if not crumbs:
        return '', None
    items = [('Home', '/')] + crumbs
    html = '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + ''.join(
        (f'<li><a href="{p}">{esc(t)}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{esc(t)}</li>')
        for i, (t, p) in enumerate(items)) + '</ol></nav>'
    ld = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, "item": sp.SITE + p} for i, (t, p) in enumerate(items)]}
    return html, ld


def faq_html(faq):
    if not faq:
        return '', None
    items = ''.join(f'<details><summary>{esc(q)}</summary><p>{a}</p></details>' for q, a in faq)
    html = f'''<section class="faq" aria-labelledby="faq-title"><div class="wrap narrow">
    <h2 id="faq-title">Questions</h2>{items}</div></section>'''
    ld = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'<[^>]+>', '', a)}}
        for q, a in faq]}
    return html, ld


def related_html(paths, by_path, title='Keep exploring'):
    cards = []
    for p in paths or []:
        if p not in by_path:
            raise SystemExit(f'related link to unknown page {p}')
        r = by_path[p]
        cards.append(f'<a class="rel-card" href="{p}"><span class="rel-kicker">{esc(r.get("kicker", ""))}</span>'
                     f'<b>{esc(r.get("label", r["h1"]))}</b><span>{esc(r.get("teaser", r["description"]))}</span></a>')
    if not cards:
        return ''
    return f'''<section class="related" aria-labelledby="rel-title"><div class="wrap">
    <h2 id="rel-title">{esc(title)}</h2><div class="rel-grid">{''.join(cards)}</div></div></section>'''


def toc(body):
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    if len(heads) < 3:
        return ''
    items = ''.join(f'<li><a href="#{i}">{re.sub(r"<[^>]+>", "", t)}</a></li>' for i, t in heads)
    return f'<nav class="toc" aria-label="On this page"><b>On this page</b><ol>{items}</ol></nav>'


def inline_cta(page):
    role = page.get('role', '')
    return f'''<aside class="callout" aria-label="Chalkmind">
      <div><b>{esc(page.get("cta_title", "Try it on your own work"))}</b>
      <p>{esc(page.get("cta_text", "Chalkmind solves handwritten problems, finds the first mistake in your working and explains each step, on an Android tablet or phone."))}</p></div>
      <a class="btn btn-primary btn-small" href="{sp.cta_href()}">{sp.cta_label()}</a></aside>'''


def render(page, by_path):
    t = page['type']
    path = page['path']
    crumbs_html, crumbs_ld = breadcrumbs([tuple(c) for c in page.get('crumbs', [])])
    faq_block, faq_ld = faq_html(page.get('faq'))
    graph = []
    if crumbs_ld:
        graph.append(crumbs_ld)
    if faq_ld:
        graph.append(faq_ld)
    body = page['body'].replace('<!--cta-->', inline_cta(page))
    words = len(re.sub(r'<[^>]+>', ' ', body).split())

    if t == 'guide':
        graph.append({"@type": "Article", "headline": page['h1'], "description": page['description'],
                      "datePublished": page.get('published', page['updated']), "dateModified": page['updated'],
                      "image": sp.SITE + '/og-image.png', "mainEntityOfPage": sp.SITE + path,
                      "author": {"@type": "Organization", "name": "Chalkmind", "url": sp.SITE},
                      "publisher": {"@type": "Organization", "name": "Chalkmind", "logo": {"@type": "ImageObject", "url": sp.SITE + "/apple-touch-icon.png"}}})
        mins = max(2, round(words / 220))
        main = f'''<main id="main">
  <header class="page-hero guide-hero"><div class="wrap narrow">
    {crumbs_html}
    <span class="eyebrow">{esc(page.get("eyebrow", "Guide"))}</span>
    <h1>{page["h1"]}</h1>
    <p class="lede">{page["lede"]}</p>
    <p class="meta">{mins} min read · Updated {datetime.date.fromisoformat(page["updated"]).strftime("%-d %B %Y")}</p>
  </div></header>
  <article class="wrap narrow prose">
    {toc(body)}
    {body}
  </article>
  {faq_block}
  {related_html(page.get("related"), by_path, "Related")}
  {sp.join_section(role=page.get("role", ""))}
</main>'''
    elif t in ('landing', 'hub'):
        graph.append({"@type": "WebPage", "name": page['title'], "description": page['description'], "url": sp.SITE + path})
        second = page.get('cta2')
        second_html = f'<a class="btn btn-ghost" href="{second[1]}">{esc(second[0])}</a>' if second else ''
        visual = page.get('visual_html', '')
        hero_cls = 'page-hero has-visual' if visual else 'page-hero'
        main = f'''<main id="main">
  <header class="{hero_cls}"><div class="wrap{' hero-grid' if visual else ' narrow'}">
    <div>
    {crumbs_html}
    <span class="eyebrow">{esc(page.get("eyebrow", "Chalkmind"))}</span>
    <h1>{page["h1"]}</h1>
    <p class="lede">{page["lede"]}</p>
    {'' if t == 'hub' else f'<div class="cta-row"><a class="btn btn-primary" href="{sp.cta_href()}">{sp.cta_label()}</a>{second_html}</div>'}
    {'' if t == 'hub' else '<p class="fineprint">Android tablets and phones · Free to start · No ads</p>'}
    </div>{visual}
  </div></header>
  {body}
  {faq_block}
  {related_html(page.get("related"), by_path)}
  {sp.join_section(title=page.get("join_title", "Get early access to Chalkmind"), role=page.get("role", ""))}
</main>'''
    elif t == 'thanks':
        main = f'<main id="main" class="wrap narrow doc thanks">{body}</main>'
    else:  # doc
        main = f'<main id="main" class="wrap doc">{body}</main>'

    ld = jsonld({"@context": "https://schema.org", "@graph": graph}) if graph else ''
    robots = '\n  <meta name="robots" content="noindex">' if page.get('noindex') else ''
    og = 'article' if t == 'guide' else 'website'
    return f'''<!doctype html>
<html lang="en">
<head>
  {sp.head(page["title"], page["description"], path, og, robots + ld)}
</head>
<body class="page-{t}">
{sp.header()}
{main}
{sp.footer()}
</body>
</html>
'''


def write(path, html):
    out = os.path.join(PUBLIC, path.lstrip('/') + '.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(html)
    return out


def hw(m):
    """{{HW|text|x|y|size|class}} -> handwriting strokes (animated on scroll)."""
    from handwriting_svg import strokes
    text, x, y, h, cls = m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5)
    out = []
    t = float(cls.split(':')[1]) if ':' in cls else 0.3
    cls = cls.split(':')[0]
    for d in strokes(text, x, y, h):
        out.append(f'<path class="chalk {cls} draw" pathLength="1" style="--d:{t:.2f}s" d="{d}"/>')
        t += 0.2
    return ''.join(out)


def hub_list(pages, kind):
    items = [p for p in pages if p['type'] == kind]
    return ''.join(f'<a class="rel-card" href="{p["path"]}"><span class="rel-kicker">{esc(p.get("kicker", ""))}</span>'
                   f'<b>{esc(p.get("label", p["h1"]))}</b><span>{esc(p.get("teaser", p["description"]))}</span></a>'
                   for p in items)


def main():
    pages = load_pages()
    by_path = {p['path']: p for p in pages}
    for p in pages:
        p['body'] = p['body'].replace('{{GUIDE_LIST}}', hub_list(pages, 'guide'))
        for g in ('choose', 'study', 'teach'):
            p['body'] = p['body'].replace('{{GUIDE_LIST:' + g + '}}', hub_list([x for x in pages if x.get('group') == g], 'guide'))
        if p.get('visual'):
            v = open(os.path.join(ROOT, 'content', '_visuals', p['visual'] + '.html')).read()
            p['visual_html'] = re.sub(r'\{\{HW\|([^|]+)\|([\d.]+)\|([\d.]+)\|([\d.]+)\|([^}]*)\}\}', hw, v)
    written = []
    for p in pages:
        written.append((p, write(p['path'], render(p, by_path))))

    # Home page (shares header, footer and the early-access form).
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_index.py')], check=True)

    # Sitemap: home + every indexable page.
    urls = [('/', TODAY, '1.0')] + [(p['path'], p['updated'], p.get('priority', '0.7'))
                                    for p in pages if not p.get('noindex')]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, mod, pri in urls:
        sm.append(f'  <url><loc>{sp.SITE}{"" if path == "/" else path}</loc><lastmod>{mod}</lastmod><priority>{pri}</priority></url>')
    sm.append('</urlset>')
    open(os.path.join(PUBLIC, 'sitemap.xml'), 'w').write('\n'.join(sm) + '\n')
    total = sum(len(open(f).read().encode()) for _, f in written)
    print(f'{len(written)} pages written ({total // 1024} KB), sitemap with {len(urls)} URLs')


if __name__ == '__main__':
    main()
