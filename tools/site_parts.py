"""Shared header, footer, early-access form and <head> for every page."""
import html as _html
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SITE = 'https://chalkmind.tech'
API = 'https://api.chalkmind.tech'

# When the app is live on Google Play, set PLAY_URL and every "Get early
# access" button becomes "Get it on Google Play".
PLAY_URL = ''

LOGO = open(os.path.join(ROOT, 'public', 'favicon.svg')).read().strip().replace(
    '<svg xmlns="http://www.w3.org/2000/svg"',
    '<svg aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg"').replace(
    'id="g"', 'id="lg"').replace('url(#g)', 'url(#lg)')

esc = _html.escape


def cta_href():
    return PLAY_URL or '#join'


def cta_label():
    return 'Get it on Google Play' if PLAY_URL else 'Get early access'


def header():
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="/" aria-label="Chalkmind home">{LOGO}<span>Chalkmind</span></a>
    <ul class="nav-links">
      <li><a href="/#features">Features</a></li>
      <li><a href="/for/teachers">Teachers</a></li>
      <li><a href="/for/students">Students</a></li>
      <li><a href="/guides">Guides</a></li>
    </ul>
    <a class="btn btn-primary btn-small" href="{cta_href()}">{cta_label()}</a>
  </div>
</header>'''


FOOTER_COLS = [
    ('Product', [('/ai-whiteboard', 'AI whiteboard'), ('/handwritten-math-solver', 'Handwritten maths solver'),
                 ('/check-my-math', 'Check my work'), ('/pdf-annotation', 'PDF notes & word look-up'),
                 ('/chemical-equation-balancer', 'Chemical equations'), ('/mind-map-maker', 'Mind maps & flowcharts'),
                 ('/handwritten-notes', 'Handwritten study notes')]),
    ('Made for', [('/for/teachers', 'Teachers'), ('/for/students', 'Students'), ('/for/tutors', 'Tutors'),
                  ('/for/parents', 'Parents'), ('/subjects/algebra', 'Algebra'), ('/subjects/geometry', 'Geometry')]),
    ('Compare & learn', [('/guides/best-whiteboard-app-for-teaching', 'Best whiteboard app for teaching'),
                         ('/guides/best-apps-for-handwritten-notes-on-android', 'Best handwritten notes apps'),
                         ('/compare/microsoft-whiteboard-alternative', 'Microsoft Whiteboard alternative'),
                         ('/compare/photomath-alternative', 'Photomath alternative'),
                         ('/guides/how-to-take-notes-on-a-tablet', 'How to take notes on a tablet'),
                         ('/guides/how-to-check-your-math-homework', 'How to check maths homework'),
                         ('/guides/how-to-balance-chemical-equations', 'How to balance equations'),
                         ('/guides', 'All guides')]),
    ('Chalkmind', [('/support', 'Help & support'), ('/privacy', 'Privacy'), ('/terms', 'Terms'),
                   ('mailto:support@chalkmind.tech', 'support@chalkmind.tech')]),
]


def footer():
    cols = []
    for title, links in FOOTER_COLS:
        items = ''.join(f'<li><a href="{h}">{esc(t)}</a></li>' for h, t in links)
        cols.append(f'<div><h2>{esc(title)}</h2><ul>{items}</ul></div>')
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="foot-cols">
      <div class="foot-brand"><a class="brand" href="/">{LOGO}<span>Chalkmind</span></a>
        <p>The whiteboard that understands your handwriting. For teachers and students on Android.</p></div>
      {''.join(cols)}
    </div>
    <div class="foot">
      <span>© 2026 Chalkmind</span>
      <span>No ads. Your boards stay on your device.</span>
    </div>
  </div>
</footer>
<script src="/site.js" defer></script>'''


ROLE_OPTIONS = [('', 'I am a…'), ('teacher', 'Teacher'), ('student', 'Student'), ('parent', 'Parent'),
                ('tutor', 'Tutor'), ('other', 'Something else')]


def join_form(default_role=''):
    opts = ''.join(f'<option value="{v}"{" selected" if v == default_role and v else ""}>{esc(t)}</option>'
                   for v, t in ROLE_OPTIONS)
    return f'''<form class="join-form" action="{API}/v1/waitlist" method="post" novalidate>
        <label class="sr" for="join-email">Email address</label>
        <input id="join-email" type="email" name="email" placeholder="you@example.com" autocomplete="email" required>
        <label class="sr" for="join-role">I am a</label>
        <select id="join-role" name="role">{opts}</select>
        <input type="hidden" name="source" value="">
        <div class="hp" aria-hidden="true"><label>Website <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
        <button class="btn btn-primary" type="submit">Join the early-access list</button>
        <p class="join-msg" role="status" aria-live="polite"></p>
      </form>'''


def join_section(title='Get early access to Chalkmind', text=None, role=''):
    if PLAY_URL:
        return f'''<section class="final join" id="join" aria-labelledby="join-title">
  <div class="wrap">
    <h2 id="join-title">Try Chalkmind free</h2>
    <p class="lede">Free to download. Writing, PDFs and on-device maths need no account.</p>
    <div class="cta-row"><a class="btn btn-primary" href="{PLAY_URL}">Get it on Google Play</a></div>
  </div>
</section>'''
    text = text or ('Chalkmind is in testing before its Google Play launch. Join the list and we’ll email you an '
                    'install link when it’s your turn. One email, no spam.')
    return f'''<section class="final join" id="join" aria-labelledby="join-title">
  <div class="wrap">
    <h2 id="join-title">{esc(title)}</h2>
    <p class="lede">{esc(text)}</p>
    {join_form(role)}
    <p class="fineprint">Android 7.0+ · Best on a tablet with a stylus · <a href="/privacy">Privacy</a></p>
  </div>
</section>'''


def head(title, description, path, og_type='website', extra=''):
    url = SITE + path
    return f'''<meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#0b3b35">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon-48.png" sizes="48x48" type="image/png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="stylesheet" href="/styles.css">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Chalkmind">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">{extra}'''
