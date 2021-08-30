import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "-username",
    "-u",
    type=str,
    required=True,
    help="Username to login as.",
)
argparser.add_argument(
    "-password",
    "-p",
    type=str,
    required=True,
    help="Password for the user.",
)
argparser.add_argument(
    "-keyword",
    "-k",
    type=str,
    required=True,
    help="Keyword to search for jobs by.",
)
argparser.description = "Automatically apply for jobs on Dice."
args = argparser.parse_args()

SEARCH_URL_WITHOUT_PAGE = f"https://www.dice.com/jobs?q={args.keyword}&countryCode=US&radius=30&radiusUnit=mi&page=%s&pageSize=100&filters.postedDate=ONE&filters.employmentType=THIRD_PARTY&filters.easyApply=true&language=en"
WAIT_TIME_S = 3

# Create webdriver, add user data to persist login and not have to relog
options = Options()
# TODO: will remove data dir for final script
options.add_argument("user-data-dir=c:/tmp/chrome_data")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, WAIT_TIME_S)

# TODO: uncomment after testing
# log in
# driver.get("https://www.dice.com/dashboard/login")
# # wait for login elements to appear
# try:
#     elem = wait.until(EC.presence_of_element_located((By.ID, "email")))
#     elem.send_keys(f"{args.email}\t{args.password}{Keys.RETURN}")
# except:
#     print("Don't need to log in. Continuing.")

# iterate through pages until there are no links
page_number = 1
while True:
    search_url = SEARCH_URL_WITHOUT_PAGE % page_number
    page_number += 1
    driver.get(search_url)
    try:
        search_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.search-card"))
        )
    except:
        print("No jobs found within wait limit.")
        break
    # wait for ribbons to appear so we know what we've applied to
    ribbons = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.ribbon-inner"))
    )
    for card in search_cards:
        print(card.text)
        link = card.find_element_by_css_selector("a.card-title-link")
        print(f"Applying to {link.text}")
        try:
            ribbon = card.find_element_by_css_selector("span.ribbon-inner")
            if ribbon and ribbon.text == "applied":
                print("Already applied.")
                continue
        except:
            ...
        job_url = link.get_attribute("href")
        driver.get(job_url)
        quit()
