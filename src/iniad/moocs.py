from dataclasses import dataclass
from typing import Iterator

from bs4 import BeautifulSoup

from iniad.course import Course
from iniad.iniad import Iniad
from iniad.lecture import Lecture
from iniad.page import Page
from iniad.url import MoocsURL


@dataclass
class Moocs(Iniad):
    # path: str

    def __post_init__(self):
        super().__post_init__()
        self.path = "https://moocs.iniad.org"
        self.login_moocs()

    def courses(self) -> Iterator[Course]:
        response = self.session.get(self.path + "/courses")
        soup = BeautifulSoup(response.text, "html.parser")
        courses = soup.select("section.content .media")
        for course in courses:
            name = course.select_one("h4").text
            prefix = course.select_one("a")["href"]
            yield Course(name, prefix, self.session)

    def course(self, url: str) -> Course:
        u = MoocsURL(url)
        prefix = u.prefix("course")
        url = self.path + prefix
        response = self.session.get(url)
        if response.url != url:
            raise ValueError("Invalid URL")

        soup = BeautifulSoup(response.text, "html.parser")
        name = soup.select_one("h1").text
        return Course(name, prefix, self.session)

    def lecture(self, url: str) -> Lecture:
        course = self.course(url)
        lecture = course.lecture(url)
        return lecture

    def page(self, url: str) -> Page:
        lecture = self.lecture(url)
        page = lecture.page(url)
        return page
