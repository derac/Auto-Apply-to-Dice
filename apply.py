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
argparser.add_argument(
    "-resume_path",
    "-r",
    type=str,
    required=True,
    help="Resume PDF to send for the job applications.",
)
argparser.add_argument(
    "-cache",
    "-c",
    type=str,
    default="",
    help="Directory to cache browser session in, so you stay logged in.",
)
argparser.add_argument(
    "-wait_s",
    "-w",
    type=int,
    default=3,
    help="Number of seconds to wait for selenium to find things.",
)
argparser.description = "Automatically apply for jobs on Dice."
args = argparser.parse_args()

SEARCH_URL_WITHOUT_PAGE = f"https://www.dice.com/jobs?q={args.keyword}&countryCode=US&radius=30&radiusUnit=mi&page=%s&pageSize=100&filters.postedDate=ONE&filters.employmentType=THIRD_PARTY&filters.easyApply=true&language=en"

# Create webdriver, add user data to persist login and not have to relog
options = Options()
if args.cache:
    options.add_argument("user-data-dir=" + args.cache)
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, args.wait_s)

# log in
driver.get("https://www.dice.com/dashboard/login")
try:
    elem = wait.until(EC.presence_of_element_located((By.ID, "email")))
    elem.send_keys(f"{args.username}\t{args.password}{Keys.RETURN}")
except Exception as e:
    print(e)
    print("Don't need to log in. Continuing.")

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
    except Exception as e:
        print(e)
        print("No jobs found within wait limit.")
        break
    # wait for ribbons to appear (if there are ribbons)
    try:
        ribbons = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.ribbon-inner"))
        )
    except:
        ...
    for card in search_cards:
        link = card.find_element_by_css_selector("a.card-title-link")
        print(f"Applying to {link.text}")
        try:
            ribbon = card.find_element_by_css_selector("span.ribbon-inner")
            if ribbon.text == "applied":
                print("Already applied.")
                continue
        except:
            ...
        job_url = link.get_attribute("href")
        driver.get(job_url)
        apply_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dhi-wc-apply-button"))
        )
        # wait for apply container to say Apply Now
        wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "dhi-wc-apply-button"), "Apply Now"
            )
        )
        # click on apply button
        driver.execute_script(
            "arguments[0].shadowRoot.querySelector('button').click();", apply_container
        )
        # wait for upload a resume radio to be visible
        resume_radio = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input#upload-resume-radio")
            )
        )
        resume_radio.click()
        # enter file location into file input
        resume_file_input = driver.find_element_by_css_selector(
            "input#upload-resume-file-input"
        )
        resume_file_input.send_keys(args.resume_path)
        submit_job_button = driver.find_element_by_css_selector("button#submit-job-btn")
        submit_job_button.click()

        # TODO: finish script and remove quit
        quit()
