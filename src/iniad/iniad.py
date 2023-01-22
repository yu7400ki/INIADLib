import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class Iniad:
    username: str
    password: str

    def __post_init__(self):
        self.session = requests.Session()

    def login_account(self) -> requests.Session:
        login_url = "https://accounts.iniad.org/"
        self.__login(login_url)
        return self.session

    def login_moocs(self) -> requests.Session:
        login_url = "https://moocs.iniad.org/auth/iniad/"
        self.__login(login_url)
        return self.session

    def login_google(self) -> requests.Session:
        login_url = "https://accounts.google.com/samlredirect?domain=iniad.org"
        response = self.__login(login_url)
        session = self.session

        soup = BeautifulSoup(response.text, "html.parser")
        form = soup.select_one("form[name='saml-post-binding']")
        action = form["action"]
        SAMLResponse = form.select_one("input[name='SAMLResponse']")["value"]
        RelayState = form.select_one("input[name='RelayState']")["value"]
        payload = {
            "SAMLResponse": SAMLResponse,
            "RelayState": RelayState,
        }
        response = session.post(action, data=payload)

        soup = BeautifulSoup(response.text, "html.parser")
        a = soup.select_one("a")
        href = a["href"]
        response = session.get(href)

        soup = BeautifulSoup(response.text, "html.parser")
        meta = soup.select_one("noscript > meta")
        content = meta["content"]
        url = re.search(r"url=(.+)", content).group(1).replace("&amp;", "&")
        session.get(url)

        return session

    def __login(self, login_url: str) -> requests.Response:
        session = self.session
        login_page = session.get(login_url)

        url = login_page.url
        if url == "https://moocs.iniad.org/courses":
            return login_page
        elif url == "https://accounts.iniad.org/auth/realms/master/account":
            return login_page

        soup = BeautifulSoup(login_page.text, "html.parser")

        text_center = soup.select_one("h1.text-center")
        if text_center.text == "Authentication Redirect":
            return login_page

        form = soup.select_one(".form-signin")
        action = form["action"]

        payload = {
            "username": self.username,
            "password": self.password,
        }

        response = session.post(action, data=payload)

        soup = BeautifulSoup(response.text, "html.parser")
        media_body = soup.select_one(".media-body")
        if media_body is not None and media_body.text == "Invalid username or password.":
            raise ValueError(media_body.text)

        return response
