import json
import pandas as pd

data_dir = "../../../data/clean"

def convert_text_to_dict(entity_name, output):
        qas = output.split('\n\n')
        qas_dict = {"name": entity_name, "QA": []}

        # TODO: propose more strict way to extract question and answer
        for qa in qas:
            question, answer = qa.split('\n')
            qas_dict["QA"].append({"Q": question[3:], "A": answer[3:]})

        return qas_dict

# TODO: if I can, solve the dependency of csv 
def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"
        with open(f"{category_dir}/csv/entity_ids_names.csv") as f:
            df = pd.read_csv(f)
        qa_of_entities = {}
        for entity_id, entity_name in zip(df["wikidata_id"], df["entity_name"]):
            with open(f"{category_dir}/gpt_3_output/{entity_id}.txt", 'r') as f:
                output = f.read()
            if output:
                qa_of_entities[entity_id] = convert_text_to_dict(entity_name, output)
        with open(f"{category_dir}/qa_of_entities.json", 'w') as f:
            json.dump(qa_of_entities, f, indent=2)

if __name__ == "__main__":
    main()