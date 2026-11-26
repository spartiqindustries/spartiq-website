"""Build ar/index.html (Arabic, right-to-left) from index.html using tools/ar_strings.py.
Run from the repo root:  python3 tools/build_ar.py"""
import re, os, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from ar_strings import T, CONTEXT, JS

src = open('index.html', encoding='utf-8').read()
s = src
# no-wrap helpers are only for English hyphens/phrases; drop them before translating
s = re.sub(r'<span class="nw">(.*?)</span>', r'\1', s)
for a, b in CONTEXT:
    s = s.replace(a, b)

# split off <style> and <script> so only page text is translated
parts = re.split(r'(<style>.*?</style>|<script>.*?</script>)', s, flags=re.S)
missing = set()
def tr_text(m):
    raw = m.group(1); t = raw.strip()
    if not t or not re.search(r'[A-Za-z]', t): return m.group(0)
    key = t if t in T else html.unescape(t)
    if key in T:
        return '>' + raw.replace(t, html.escape(T[key], quote=False)) + '<'
    missing.add(t); return m.group(0)
def tr_attr(m):
    k, v = m.group(1), m.group(2)
    return f'{k}="{T.get(v, v)}"'
for i, p in enumerate(parts):
    if p.startswith('<style>') or p.startswith('<script>'): continue
    p = re.sub(r'>([^<]+)<', tr_text, p)
    p = re.sub(r'(placeholder|aria-label|content)="([^"]+)"', tr_attr, p)
    parts[i] = p
s = ''.join(parts)

# script strings
for a, b in JS:
    if a not in s: print('JS string not found:', a)
    s = s.replace(a, b)

# language, direction and switch back to English
s = s.replace('<html lang="en">', '<html lang="ar" dir="rtl">', 1)
s = s.replace('lang="en" hreflang="en" class="on" aria-current="true">EN</a>', 'lang="en" hreflang="en">EN</a>')
s = s.replace('lang="ar" hreflang="ar">عربي</a>', 'lang="ar" hreflang="ar" class="on" aria-current="true">عربي</a>')

# Arabic typography and right-to-left adjustments
css = '''
/* ===== Arabic / RTL ===== */
:root{--font-display:"IBM Plex Sans Arabic","Chakra Petch",sans-serif;--font-sans:"IBM Plex Sans Arabic","IBM Plex Sans",sans-serif;--font-mono:"IBM Plex Sans Arabic","IBM Plex Mono",monospace}
html[lang="ar"] body *:not(.lang-toggle a[lang="en"]){letter-spacing:0!important;text-transform:none!important}
.sq-route,.sq-card__spec code,.spec code,.ct .mail{direction:ltr;unicode-bidi:isolate}
.logo,footer svg{direction:ltr}
.hero canvas{transform:scaleX(-1)}
.flow li{padding:var(--space-6) 0 0 var(--space-6)}
.flow li::before{left:auto;right:0}
.list li{padding:14px 44px 14px var(--space-6)}
.list li::before{left:auto;right:var(--space-6)}
.ticks li,.locs li{padding-left:0;padding-right:22px}
.ticks li::before,.locs li::before{left:auto;right:2px}
.spec th,.spec td{text-align:right}
@media (max-width:1200px){.nav a.nl::after{content:"←"}}
.menu-btn{padding:12px 8px 12px 0}
.sq-eyebrow::before{content:"//"}
h1,h2,h3{line-height:1.25}
.display{line-height:1.2}
.big{line-height:1.7}
.lang-toggle{right:auto;left:0;border-right:1px solid var(--graphite-line);border-left:0}
.nav a.nl{font-size:15px}
.nav .sq-btn,.sq-btn{font-size:15px}
.sq-eyebrow,.crumb,.sq-card__num,.flow .n,.fparent,.fbase,.fcols .t,.hero .meta{font-size:13px}
'''
s = s.replace('</style>', css + '</style>', 1)

os.makedirs('ar', exist_ok=True)
open('ar/index.html', 'w', encoding='utf-8').write(s)
keep = {'EN','Spartiq','IN','US','UK','EU','SA','AE','CN','EN 10204 3.1','sales@spartiq.com','spartiq.com'}
left = sorted(m for m in missing if m not in keep)
print('ar/index.html written;', len(left), 'untranslated:', left)
