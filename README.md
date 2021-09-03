# Auto Apply to Dice

Automatically apply to jobs on Dice. Enter username, password, the search keyword, and your resume path. This only works for Easy apply jobs.

# Usage

1. Install Python 3 and make sure it's in your path.
1. Install chromedriver for selenium, you can put it in your path or in this directory, you need the proper version for your install of chrome - https://sites.google.com/chromium.org/driver/downloads
1. cd to this directory in your terminal. `cd`
1. install requirements. `pip install -r requirements.txt`
1. `python3 ./apply.py -u <USERNAME> -p <PASSWORD> -k <KEYWORD> -r <RESUME PATH>`

## Command parameters

```
usage: apply.py [-h] -username USERNAME -password PASSWORD -keyword KEYWORD -resume_path RESUME_PATH [-cache_path CACHE_PATH] [-wait_s WAIT_S]

Automatically apply for jobs on Dice.

optional arguments:
  -h, --help            show this help message and exit
  -username USERNAME, -u USERNAME
                        Username to login as.
  -password PASSWORD, -p PASSWORD
                        Password for the user.
  -keyword KEYWORD, -k KEYWORD
                        Keyword to search for jobs by.
  -resume_path RESUME_PATH, -r RESUME_PATH
                        Resume PDF to send for the job applications.
  -cache_path CACHE_PATH, -c CACHE_PATH
                        Directory to cache browser session in, so you stay logged in.
  -wait_s WAIT_S, -w WAIT_S
                        Number of seconds to wait for selenium to find things.
```
