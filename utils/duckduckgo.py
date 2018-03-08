import aiohttp

from urllib.parse import quote
from bs4 import BeautifulSoup

_http = aiohttp.ClientSession()
_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"


class SearchResult:
    def __init__(self, title, description, url):
        self.title = title
        self.description = description
        self.url = url


async def search(query: str, locale="uk-en", timeout=30, proxy=None, count=3, safe=-2):
    if not query:
        raise ValueError("query must be defined")

    async with _http.get(f"https://duckduckgo.com/html/?q={quote(query)}&kr={locale}&kp={safe}",
                         timeout=timeout,
                         proxy=proxy,
                         headers={'User-Agent': _user_agent}) as page:

        p = await page.read()

        parse = BeautifulSoup(p, 'html.parser')
        results = parse.findAll('div', attrs={'class': 'result__body'})

        res = []

        if parse.findAll('div', attrs={'class': 'no-results'}):
            return res

        for result in results[:count]:
            anchor = result.find('a')
            title = anchor.get_text()
            url = anchor.get('href')
            description = result.find(class_='result__snippet').get_text()
            sr = SearchResult(title, description, url)
            res.append(sr)

        return res


def _shutdown():
    _http.close()
