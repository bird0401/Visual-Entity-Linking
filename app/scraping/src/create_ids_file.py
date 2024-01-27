from app.scraping.src.config import *
import os
import json

def create_ids_file(category):
    category_dir = get_category_dir(category)
    wikipedia_dir = f"{category_dir}/wikipedia"
    article_files = os.listdir(wikipedia_dir)
    ids = []
    for article_file in article_files:
        ids.append(article_file.replace(".txt", ""))
    ids.sort()
    with open(f"{category_dir}/ids.json", "w") as f:
        json.dump(ids, f, indent=4)

def main():
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    categories = ["aircraft"]
    for category in categories:
        create_ids_file(category)

if __name__ == "__main__":
    main()