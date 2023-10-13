import pandas
import pickle

def main():
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        print(f"category: {category}")
        category_dir = f"../../../data/clean/{category}"
        df = pandas.read_csv(f"{category_dir}/csv/entity_ids_names.csv")
        id_to_name = {}
        for entity_id, entity_name in zip(df["wikidata_id"], df["entity_name"]):
            id_to_name[entity_id] = entity_name
        print(f"len(id_to_name): {len(id_to_name)}")
        print("list(id_to_name.items())[:10]")
        print(list(id_to_name.items())[:10])
        with open(f"{category_dir}/id_to_name.pkl", 'wb') as f:
            pickle.dump(id_to_name, f)

if __name__ == "__main__":
    main()