import sys
sys.path.append("utils")

from extract_relations import extract_relations_from_wikidata_by_categories
from relations_to_text import relations_to_text_by_categories

def main():
    # categories = ["athlete"]
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # print("Start extract_relations ...")
    # extract_relations_from_wikidata_by_categories(categories)
    print("Start relations_to_text ...")
    relations_to_text_by_categories(categories)
    print("Finish")

if __name__ == "__main__":
    main()
    