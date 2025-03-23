
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def configure_webdriver():
    """Return a configured headless Chrome webdriver."""
    options = Options()
    options.add_argument('--headless')
    service = Service('/Users/gilbertyoung/Downloads/chromedriver-mac-arm64/chromedriver')
    return webdriver.Chrome(service=service, options=options)
