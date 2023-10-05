import openai
import os, json, pickle
from util import *

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def mask_entity_name_by_category(category, entity_name, text):
    messages=[
        {"role": "system", "content": "You are a helpful annotator of sentences."},
        {"role": "user", "content": f"Please convert entity name of following sentences to 'the {category}'. Entity name is {entity_name}.\n\nsentences:\n{text}\n\n"},
    ]
    # print(messages[1]["content"])
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    return response.choices[0]["message"]["content"]

def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"
        with open(f"{category_dir}/qa_rephrase.json") as f:
            qa_of_entities = json.load(f)
        with open(f"{category_dir}/id_to_name.pkl", 'rb') as f:
            id_to_name = pickle.load(f)

        for entity_id in qa_of_entities:
            questions_merge = merge_text(qa_of_entities[entity_id], "Q_rephrase")
            questions_masked = mask_entity_name_by_category(category, id_to_name[entity_id], questions_merge)
            questions_masked_list = questions_masked.split("\n")
            for i in range(len(qa_of_entities[entity_id])):
                qa_of_entities[entity_id][i]["Q_rephrase_mask"] = questions_masked_list[i]
            
        with open(f"{category_dir}/qa_rephrase_mask.json", 'w') as f:
            json.dump(qa_of_entities, f, indent=2)

if __name__ == "__main__":
    main()

