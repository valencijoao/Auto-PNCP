import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def criar_sessao():

    session = requests.Session()

    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=2,
        status_forcelist=[500,502,503,504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount("http://",adapter)
    session.mount("https://",adapter)

    session.headers.update({
        "User-Agent":"Mozilla/5.0",
        "Accept":"application/json"
    })

    return session