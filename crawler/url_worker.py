import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse


class UrlWorker:
    def __init__(self, url: str):
        self.url = url
        parts = urlparse(url)
        self.netloc = parts.netloc

    def _fetch_content(self) -> str:
        response = requests.get(self.url)
        return response.text

    def _extract_href(self, href) -> str | None:
        href = href.rstrip("/")
        parts = urlparse(href)

        # it the netloc is different we want to return none to not end up on another site
        if parts.netloc and parts.netloc != self.netloc:
            return None

        # This doesn't lead anywhere interesting
        if not parts.path and not parts.params:
            return None

        if any([parts.scheme == s for s in ["tel", "mailto"]]):
            return None

        # Is this an image or some other non-important thing?
        if any([parts.path.endswith(ext) for ext in [".png"]]):
            return None

        # if there is no netloc, we need to reconstruct a full url.
        if not parts.netloc:
            print(f"Handle {parts} for parent url {self.url}")
            # TODO impl
            return None

        return href

    def _extract_urls(self, content) -> list[str]:
        soup = BeautifulSoup(content, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            if isinstance(a, Tag):
                href = self._extract_href(a["href"])
                if href:
                    links.append(href)

        return links

    def run(self) -> list[str]:
        """
        Process the URL and return all the sub urls
        """
        print(f"Processing {self.url}")
        try:
            content = self._fetch_content()
            urls = self._extract_urls(content)
            return urls
        except Exception as e:
            print(f"Something went wrong: {e}")

            return []
