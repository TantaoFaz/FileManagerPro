import urllib.request, urllib.parse, re

def search_ddg(query, page=1):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html',
        'Accept-Language': 'pt-BR',
    }
    data = urllib.parse.urlencode({
        'q': query,
        's': str(max(0, (page-1)*10)),
        'v': 'l',
        'o': 'json',
        'dc': str(max(0, (page-1)*10)),
    }).encode()
    req = urllib.request.Request(
        'https://lite.duckduckgo.com/lite/',
        data=data,
        headers=headers
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode('utf-8', errors='ignore')

    results = []
    links = list(re.finditer(
        r"href=\"(https?://[^\"]+)\"\s+class='result-link'>(.*?)</a>",
        html, re.DOTALL
    ))
    snippets = re.findall(r"class='result-snippet'>(.*?)</td>", html, re.DOTALL)
    for i, m in enumerate(links[:10]):
        url   = m.group(1)
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        desc  = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ''
        results.append({'title': title, 'url': url, 'description': desc})
    return results
