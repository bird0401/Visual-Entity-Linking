import json, os, pickle

data_dir = "../../../data/clean"

# def convert_text_to_dict(entity_name, output):
#         qas = output.split('\n\n')
#         qas_dict = {"name": entity_name, "QA": []}

#         # TODO: propose more strict way to extract question and answer
#         for qa in qas:
#             question, answer = qa.split('\n')
#             qas_dict["QA"].append({"Q": question[3:], "A": answer[3:]})

#         return qas_dict

def convert_text_to_dict(output):
        qas = output.split('\n\n')
        qas_dict_list = []

        # TODO: propose more strict way to extract question and answer
        for qa in qas:
            question, answer = qa.split('\n')
            qas_dict_list.append({"Q": question[3:], "A": answer[3:]})

        return qas_dict_list

def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"
        # with open(f"{category_dir}/csv/entity_ids_names.csv") as f:
        #     df = pd.read_csv(f)
        with open(f"{category_dir}/id_to_name.pkl", 'rb') as f:
            id_to_name = pickle.load(f)
        entity_text_files = os.listdir(f"{category_dir}/gpt_3_output")
        qa_of_entities = {}
        for entity_text_file in entity_text_files:
            entity_id = entity_text_file.split(".")[0]
            entity_name = id_to_name[entity_id]
            with open(f"{category_dir}/gpt_3_output/{entity_text_file}", 'r') as f:
                output = f.read()
            if output:
                qa_of_entities[entity_id] = convert_text_to_dict(output)
        with open(f"{category_dir}/qa.json", 'w') as f:
            json.dump(qa_of_entities, f, indent=2)

if __name__ == "__main__":
    main()