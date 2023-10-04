import pandas
import pickle

def main():
    df = pandas.read_csv("../../../data/clean/athlete/csv/entity_ids_names.csv")
    id_to_name = {}
    for entity_id, entity_name in zip(df["wikidata_id"], df["entity_name"]):
        id_to_name[entity_id] = entity_name
    print(id_to_name)
    with open("../../../data/clean/athlete/id_to_name.pkl", 'wb') as f:
        pickle.dump(id_to_name, f)

if __name__ == "__main__":
    main()