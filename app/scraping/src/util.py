from tenacity import retry, stop_after_attempt, wait_exponential
import requests
from requests.exceptions import Timeout
import time, os
import traceback
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


def to_abs_url(base_url="https://commons.wikimedia.org", related_url="/wiki/Category"):
    return base_url + related_url


ua = UserAgent()
# ua = UserAgent(use_cache_server=False)
header = {"user-agent": ua.chrome}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def fetch(url):
    try:
        res = requests.get(url, headers=header, timeout=10)
    except Timeout:
        print("Timeout has been raised.")
        return None
    except Exception:
        traceback.print_exc()
        return None
    time.sleep(1)
    return res


# delete all exif data
def delete_exif(paths):
    for path in paths:
        try:
            src = Image.open(path)
            dst = Image.new(src.mode, src.size)
            dst.putdata(src.getdata())
            dst.convert("RGB").save(path)
        except Exception:
            print(path)
            traceback.print_exc()

def make_dir(dir_name):
    try:
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
    except Exception:
        traceback.print_exc()

def parse_to_soup(url):
    try:
        res = fetch(url)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup
    except Exception:
        traceback.print_exc()

def download_text(text, save_file_path):
    try:
        with open(save_file_path, "w") as f:
            f.write(text) 
    except Exception:
        traceback.print_exc()