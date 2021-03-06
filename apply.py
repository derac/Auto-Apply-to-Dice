import json
import os
import argparse
from itertools import count
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


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
    "-keywords",
    "-k",
    type=str,
    nargs="+",
    required=True,
    help="Keywords to search for jobs by, will be split by space then ANDed together.",
)
argparser.add_argument(
    "-blacklist",
    "-b",
    type=str,
    nargs="+",
    default=[],
    help="Keyword blacklist, will be split by space then ANDed together.",
)
argparser.add_argument(
    "-resume_path",
    "-r",
    type=str,
    required=True,
    help="Absolute path to resume file to send for the job applications.",
)
argparser.add_argument(
    "-cache_path",
    "-c",
    type=str,
    default="",
    help="Directory to cache browser session in, so you stay logged in.",
)
argparser.add_argument(
    "-wait_s",
    "-w",
    type=int,
    default=5,
    help="Number of seconds to wait for selenium to find things.",
)
argparser.description = "Automatically apply for jobs on Dice."
args = argparser.parse_args()
args.resume_path = os.path.abspath(args.resume_path)

SEARCH_URL_WITHOUT_PAGE = f"https://www.dice.com/jobs?q={' '.join(args.keywords)}&countryCode=US&radius=30&radiusUnit=mi&page=%s&pageSize=100&filters.postedDate=ONE&filters.employmentType=THIRD_PARTY&filters.easyApply=true&language=en"

# see if any data exists for this user
USER_DATA_PATH = os.path.join("cached_data", f"{args.username}.json")
completed_jobs = []
if not os.path.exists("cached_data"):
    os.mkdir("cached_data")
if os.path.exists(USER_DATA_PATH):
    with open(USER_DATA_PATH, "r") as file_handle:
        completed_jobs = json.loads(file_handle.read())
        # dictionary of {job_id: applied boolean}

# Create webdriver, add user data to persist login and not have to relog
options = Options()
if args.cache_path:
    options.add_argument("user-data-dir=" + args.cache_path)
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
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
for page_number in count(1):
    search_url = SEARCH_URL_WITHOUT_PAGE % page_number
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
    job_urls = []
    for card in search_cards:
        link = card.find_element_by_css_selector("a.card-title-link")
        job_id = link.get_attribute("id")
        if job_id in completed_jobs:
            continue
        try:
            ribbon = card.find_element_by_css_selector("span.ribbon-inner")
            if ribbon.text == "applied":
                continue
        except:
            ...
        job_urls.append((job_id, link.text, link.get_attribute("href")))

    for job_id, job_text, job_url in job_urls:
        print(f"Applying to {job_text}.")
        if not all(kw.lower() in job_text.lower() for kw in args.keywords):
            print("All keywords were not in the job title, skipping.")
            continue
        if any(kw.lower() in job_text.lower() for kw in args.blacklist):
            print("Blacklisted word found in job title, skipping.")
            continue
        driver.get(job_url)
        # wait for apply container to say Apply Now
        try:
            apply_container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "dhi-wc-apply-button"))
            )
            wait.until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "dhi-wc-apply-button"), "Apply Now"
                )
            )
            # click on apply button
            driver.execute_script(
                "arguments[0].shadowRoot.querySelector('button').click();",
                apply_container,
            )

            # wait for upload a resume radio to be visible
            resume_radio = wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input#upload-resume-radio")
                )
            )
            # check to see if the daily limit exceeded message is shown
            daily_limit = driver.find_element_by_css_selector(
                "div[id^=googleCaptchaSection]"
            )
            if daily_limit.is_displayed():
                print("Daily limit reached.")
                quit()

            apply_now_button = driver.find_element_by_css_selector(
                "button#submit-job-btn"
            )

            # enter resume info
            resume_radio.click()
            # enter file location into file input
            resume_file_input = driver.find_element_by_css_selector(
                "input#upload-resume-file-input"
            )
            resume_file_input.send_keys(args.resume_path)

            is_captcha_on = driver.find_element_by_css_selector(
                'input[name="isGoogleCaptchaOn"]'
            )
            driver.execute_script(
                "arguments[0].setAttribute('value','false')", is_captcha_on
            )

            apply_now_button.click()
        except Exception as e:
            print("Applying to this job failed with error:", e)
        # job is done processing
        completed_jobs.append(job_id)
        with open(USER_DATA_PATH, "w") as file_handle:
            file_handle.write(json.dumps(completed_jobs))
