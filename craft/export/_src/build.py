import json, re, sys, os
S=os.path.dirname(os.path.abspath(__file__))
SITE='/Users/nataliianovykova/projects/teamof3andd.github.io'
tpl=open(f'{S}/template.html',encoding='utf-8').read()
en=json.load(open(f'{S}/en.json',encoding='utf-8'))
LANGS={'en':'English','uk':'Українська','de':'Deutsch','es':'Español','fr':'Français','it':'Italiano','ja':'日本語','ko':'한국어','pl':'Polski','pt':'Português','ru':'Русский','tr':'Türkçe','vi':'Tiếng Việt','zh':'简体中文','zh-hant':'繁體中文'}
HTMLLANG={'zh':'zh-Hans','zh-hant':'zh-Hant'}
def skeleton(s):
    return re.findall(r'<[^>]+>', s)
def codes(s):
    return sorted(re.findall(r'<code>(.*?)</code>', s))
def validate(lang, tr):
    errs=[]
    if set(tr)!=set(en): errs.append(f'keys differ: missing {set(en)-set(tr)} extra {set(tr)-set(en)}')
    for k in en:
        if k not in tr: continue
        if sorted(skeleton(en[k]))!=sorted(skeleton(tr[k])): errs.append(f'{k}: tag skeleton differs')
        if codes(en[k])!=codes(tr[k]): errs.append(f'{k}: <code> content differs')
        if '{{' in tr[k] or '}}' in tr[k]: errs.append(f'{k}: braces')
    return errs
def switcher(cur):
    items=[]
    for code,name in LANGS.items():
        href='/craft/export/' if code=='en' else f'/craft/export/{code}/'
        items.append(f'<b>{name}</b>' if code==cur else f'<a href="{href}">{name}</a>')
    return '<div class="langs">'+' · '.join(items)+'</div>'
def hreflangs():
    out=[]
    for code in LANGS:
        href='https://teamof3andd.com/craft/export/' if code=='en' else f'https://teamof3andd.com/craft/export/{code}/'
        out.append(f'<link rel="alternate" hreflang="{HTMLLANG.get(code,code)}" href="{href}">')
    out.append('<link rel="alternate" hreflang="x-default" href="https://teamof3andd.com/craft/export/">')
    return '\n'.join(out)
def render(lang, tr):
    html=tpl
    for k,v in tr.items(): html=html.replace('{{'+k+'}}', v)
    if lang=='en':
        canonical='https://teamof3andd.com/craft/export/'
    else:
        canonical=f'https://teamof3andd.com/craft/export/{lang}/'
        html=html.replace('<html lang="en">', f'<html lang="{HTMLLANG.get(lang,lang)}">')
        html=html.replace('src="img/', 'src="../img/')
    html=html.replace('<link rel="canonical" href="https://teamof3andd.com/craft/export/">', f'<link rel="canonical" href="{canonical}">\n'+hreflangs())
    # language switcher under the nav
    html=html.replace('</nav>\n', '</nav>\n'+switcher(lang)+'\n',1)
    html=html.replace('footer{padding:30px 0 50px;', '.langs{max-width:820px;margin:10px auto 0;padding:0 20px;font-size:13px;color:var(--grey);line-height:1.9}.langs a{color:var(--grey)}.langs b{color:var(--ink)}\nfooter{padding:30px 0 50px;',1)
    assert '{{' not in html, re.findall(r'\{\{[^}]+\}\}', html)[:3]
    return html
langs=sys.argv[1:] or [l for l in LANGS if os.path.exists(f'{S}/{l}.json')]
ok=True
for lang in langs:
    tr=json.load(open(f'{S}/{lang}.json',encoding='utf-8'))
    errs=validate(lang,tr)
    if errs: ok=False; print(lang,'ERRORS:'); [print('  ',e) for e in errs]; continue
    out = f'{SITE}/craft/export/index.html' if lang=='en' else f'{SITE}/craft/export/{lang}/index.html'
    os.makedirs(os.path.dirname(out),exist_ok=True)
    open(out,'w',encoding='utf-8').write(render(lang,tr))
    print(lang,'ok ->',os.path.relpath(out,SITE))
sys.exit(0 if ok else 1)
