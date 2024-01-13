import json

def create_id_to_name(category):
    category_dir = f"../../../data/clean/{category}"
    # with open(f"{category_dir}/wikidata_with_commons.json") as f:
    with open(f"{category_dir}/wikidata_filtered.json") as f:
        wikidata = json.load(f)
    id_to_name = {}
    for entity_id in wikidata:
        if "name" in wikidata[entity_id]["relations"] and wikidata[entity_id]["relations"]:
            id_to_name[entity_id] = wikidata[entity_id]["relations"]["name"]
        else:
            print(f"entity_id without name: {entity_id}")
            # id_to_name[entity_id] = ""
    with open(f"{category_dir}/id_to_name.json", "w") as f:
        json.dump(id_to_name, f, indent=4)


def main():
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        print(category)
        create_id_to_name(category)


if __name__ == "__main__":
    main()

