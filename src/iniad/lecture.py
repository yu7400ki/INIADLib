import re
from dataclasses import dataclass
from typing import Iterator

from bs4 import BeautifulSoup
from requests import Session

from iniad.page import Page


@dataclass
class Lecture:
    course: str
    group: str
    name: str
    prefix: str
    session: Session

    def __post_init__(self):
        self.path = "https://moocs.iniad.org"

    def pages(self) -> Iterator[Page]:
        response = self.session.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        pages_el = list(soup.select("ul.pagination > li"))[1:-1]
        lecture = self.name

        for page_el in pages_el:
            prefix = page_el.select_one("a")["href"]
            if prefix == "#":
                url = response.url
                prefix = re.search(r"/courses/\d{4}/\w{2}\d{3}/\d+/.+", url).group()
            yield Page(lecture, prefix, self.session)

    def page(self, url: str) -> Page:
        # courses/2022/IE116/01/slide <- この形式が含まれてればOK
        prefix = re.search(r"courses/\d{4}/\w{2}\d{3}/\d+/.+", url).group()
        if prefix is None:
            raise ValueError("Invalid URL")
        prefix = "/" + prefix
        url = self.path + prefix
        response = self.session.get(url)
        if response.url != url:
            raise ValueError("Invalid URL")

        return Page(self.name, prefix, self.session)

    def reload(self) -> None:
        response = self.session.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        breadcrumb = list(soup.select("ol.breadcrumb > li"))
        self.course = breadcrumb[1].text
        self.group = breadcrumb[2].text
        self.name = breadcrumb[3].text

    @property
    def url(self) -> str:
        return self.path + self.prefix
