from tenacity import retry, stop_after_attempt, wait_exponential
import requests
from requests.exceptions import Timeout
import time, os
import traceback
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

def create_id_file():
    data_dir = "../../../data/clean"
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        csv_dir = f"{data_dir}/{category}/csv"
        df = pd.read_csv(f"{csv_dir}/origin.csv", dtype={"wikidata_id": str})
        print(category)
        ids = pd.DataFrame(df["wikidata_id"].unique())
        ids.columns = ["wikidata_id"]
        print((len(ids)))
        ids.to_csv(f"{csv_dir}/ids.csv")
        
def remove_empty_articles():
    # categories = ["athlete"]
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        print(category)
        category_dir = f"{data_dir}/{category}"
        entity_text_files = os.listdir(f"{category_dir}/wikipedia")
        print(f"len(entity_text_files): {len(entity_text_files)}")
        for entity_text_file in entity_text_files:
            with open(f"{category_dir}/wikipedia/{entity_text_file}") as f:
                article = f.read()
            article = article.strip()
            if not article:
                print(f"{category_dir}/wikipedia/{entity_text_file}")
                os.remove(f"{category_dir}/wikipedia/{entity_text_file}")

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

# def download_text(text, save_file_path):
#     try:
#         with open(save_file_path, "w") as f:
#             f.write(text) 
#     except Exception:
#         traceback.print_exc()