import re
from dataclasses import dataclass, field


@dataclass
class MoocsURL:
    url: str

    def __post_init__(self):
        url = self.url.strip()

        if re.match(r"^https?://", url) is None:
            self.url = "https://" + url

        if re.match(r"^https?://moocs\.iniad\.org/courses/", url) is None:
            raise ValueError("Invalid URL")

        self.url = url

        rest = re.match(r"^https?://moocs\.iniad\.org/courses/(.+)", url).group(1)

        if rest.endswith("/"):
            rest = rest[:-1]
        split = rest.split("/")
        split = (split + [None] * 4)[:4]
        self.year = split[0]
        self.course = split[1]
        self.lecture = split[2]
        self.page = split[3]

    def prefix(self, path: str) -> str:
        match path:
            case "year":
                paths = ["", "courses", self.year]
            case "course":
                paths = ["", "courses", self.year, self.course]
            case "lecture":
                paths = ["", "courses", self.year, self.course, self.lecture]
            case "page":
                paths = ["", "courses", self.year, self.course, self.lecture, self.page]
            case _:
                raise ValueError("Invalid path")

        if None in paths:
            raise ValueError("Invalid path")

        return "/".join(paths)
