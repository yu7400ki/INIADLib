from dataclasses import dataclass
from typing import Iterator

from bs4 import BeautifulSoup
from requests import Session

from iniad.page import Page
from iniad.url import MoocsURL


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
        course = self.course
        group = self.group
        lecture = self.name

        for page_el in pages_el:
            prefix = page_el.select_one("a")["href"]
            if prefix == "#":
                url = response.url
                u = MoocsURL(url)
                prefix = u.prefix("page")
            yield Page(course, group, lecture, prefix, self.session)

    def page(self, url: str) -> Page:
        u = MoocsURL(url)
        prefix = u.prefix("page")
        url = self.path + prefix
        response = self.session.get(url)
        if response.url != url:
            raise ValueError("Invalid URL")

        return Page(self.course, self.group, self.name, prefix, self.session)

    @property
    def url(self) -> str:
        return self.path + self.prefix
