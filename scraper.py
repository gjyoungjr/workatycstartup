from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import random

# Configure Chrome options to run the browser in headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')  # Comment this line to see the browser in action

# Set path to chromedriver (Make sure it is correct)
webdriver_path = '/Users/gilbertyoung/Downloads/chromedriver-mac-arm64/chromedriver'

# Create a ChromeDriver service
service = Service(webdriver_path)

# Launch Chrome browser
driver = webdriver.Chrome(service=service, options=chrome_options)

# Wait for the page to load
driver.get('https://www.ycombinator.com/launches')
wait = WebDriverWait(driver, 10)

# Store the HTML of all posts
launch_cards_html = []
num_posts = 0

while True:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    try:
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'Loader')))
    except:
        pass
    
    time.sleep(random.randint(2, 5)) 

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    launch_cards = soup.find_all('div', class_='post row align-center')

    # Only add new launch cards that were not already in the list
    for card in launch_cards[num_posts:]:
        launch_cards_html.append(str(card))
    
    num_posts = len(launch_cards_html)

    if len(launch_cards_html) == num_posts:
        break

# Quit the browser
driver.quit()

# Print the HTML of each launch card
for html in launch_cards_html:
    soup = BeautifulSoup(html, 'html.parser')

    post = {}

    # Extract company name
    company_name = soup.find('a', class_='post-company-name').text.strip()
    post['company_name'] = company_name

    # Extract description
    description = soup.find('a', class_='post-tagline').text.strip()
    post['description'] = description

    # Extract post date
    post_date = soup.find('div', class_='post-date').find('time')['datetime']
    post['post_date'] = post_date

    # Extract cohort
    cohort = soup.find('div', class_='batch-tag post-tag').text.strip()
    post['cohort'] = cohort

    # Extract tags
    tags = [tag.text.strip() for tag in soup.find_all('div', class_='post-tag')]
    post['tags'] = tags

    # Extract link
    link = 'https://www.ycombinator.com' + soup.find('a', class_='post-title')['href']
    post['link'] = link

    # Convert to JSON
    json_data = json.dumps(post, indent=2)
    print(json_data)
