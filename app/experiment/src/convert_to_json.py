import json
import pandas as pd

data_dir = "../../../data/clean"

def convert_text_to_dict(entity_id, entity_name):
        with open(f"{data_dir}/gpt_3_output/{entity_id}.txt", 'r') as f:
            output = f.read()

        qas = output.split('\n\n')
        qas_dict = {"name": entity_name, "QA": []}

        # TODO: propose more strict way to extract question and answer
        for qa in qas:
            question, answer = qa.split('\n')
            qas_dict["QA"].append({"Q": question[3:], "A": answer[3:]})

        return qas_dict

# TODO: if I can, solve the dependency of csv 
def main():
    with open(f"{data_dir}/entity.csv") as f:
        df = pd.read_csv(f)
    qa_of_entities = {}
    for entity_id, entity_name in zip(df["id"], df["name"]):
        qa_of_entities[entity_id] = convert_text_to_dict(entity_id, entity_name)
    with open(f"{data_dir}/qa_of_entities.json", 'w') as f:
        json.dump(qa_of_entities, f, indent=2)

if __name__ == "__main__":
    main()