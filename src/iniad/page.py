import re
from dataclasses import dataclass
from typing import Iterator

from bs4 import BeautifulSoup
from requests import Session

slide_pattern = re.compile(r"^https?://docs.google.com/presentation/d/.*?/embed\?")
svg_pattern = re.compile(r"\\x3csvg.*?\\x3c\\/svg\\x3e", re.DOTALL)


@dataclass
class Page:
    course: str
    group: str
    lecture: str
    # name: str
    # slides: list[str]
    # has_assignment: bool
    prefix: str
    session: Session

    def __post_init__(self):
        self.path = "https://moocs.iniad.org"
        response = self.session.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        h2 = soup.select_one("h2")
        bookmarker = h2.select_one("div.pull-right")
        bookmarker.decompose()
        self.name = h2.text
        self.slides = [slide["src"] for slide in soup.select("iframe") if slide_pattern.match(slide["src"])]
        problem = list(soup.select("div.problem-container"))
        self.has_assignment = len(problem) > 0

    def slides2svg(self) -> Iterator[Iterator[str]]:
        for slide in self.slides:
            response = self.session.get(slide)
            soup = BeautifulSoup(response.text, "html.parser")
            html = soup.select_one("html")
            if "data-cast-api-enabled" not in html.attrs:
                raise Exception("Not logged into Google")

            res = svg_pattern.findall(response.text)
            yield map(lambda s: s.replace("\\/", "/").encode().decode("unicode_escape"), res)

    @property
    def url(self) -> str:
        return self.path + self.prefix
