import re
from dataclasses import dataclass
from typing import Iterator

from bs4 import BeautifulSoup
from requests import Session

from iniad.lecture import Lecture


@dataclass
class Course:
    name: str
    prefix: str
    session: Session
    # path: str

    def __post_init__(self):
        self.path = "https://moocs.iniad.org"

    def lectures(self) -> Iterator[Lecture]:
        response = self.session.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        groups_el = soup.select("ul.sidebar-menu > li.treeview")

        for group_el in groups_el:
            a = group_el.select_one("a")

            if a["href"] == "/courses/bookmarks":
                continue

            group = a.text
            lectures_el = group_el.select("ul.treeview-menu > li")

            for lecture_el in lectures_el:
                course = self.name
                prefix = lecture_el.select_one("a")["href"]
                name = lecture_el.select_one("a").text
                session = self.session
                yield Lecture(course, group, name, prefix, session)

    def lecture(self, url: str) -> Lecture:
        # courses/2022/IE101/1 <- この形式が含まれてればOK
        prefix = re.search(r"courses/\d{4}/\w{2}\d{3}/.+", url).group()
        if prefix is None:
            raise ValueError("Invalid URL")
        prefix = "/" + prefix
        url = self.path + prefix
        response = self.session.get(url)
        if url + "/" not in response.url:
            raise ValueError("Invalid URL")

        soup = BeautifulSoup(response.text, "html.parser")
        breadcrumb = list(soup.select("ol.breadcrumb > li"))
        course = self.name
        group = breadcrumb[2].text
        name = breadcrumb[3].text
        session = self.session
        return Lecture(course, group, name, prefix, session)

    def reload(self) -> None:
        response = self.session.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        self.name = soup.select_one("h1").text

    @property
    def url(self) -> str:
        return self.path + self.prefix
