import openai
import os, json, pickle
from util import *

# openai.organization = os.getenv("OPENAI_ORGANIZATION")
# openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def main():
    info = {"name": True, "article": False, "relations": False, "confidence": False}
    label = ""
    for key in info:
        if info[key]:
            label += "_" + key

    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"

        with open(f"{category_dir}/qa_rephrase_mask.json") as f:
            qa_mask = json.load(f) 
        with open(f"{category_dir}/id_to_name.pkl", 'rb') as f:
            id_to_name = pickle.load(f)

        for entity_id in qa_mask:
            entity_name = id_to_name[entity_id]
            for i in range(len(qa_mask[entity_id])):
                qa_mask[entity_id][i]["A"+label] = answer(info, qa_mask[entity_id][i]["Q_rephrase_mask"], category, entity_name)
                
        with open(f"{category_dir}/answers_by_name.json", 'w') as f:
            json.dump(qa_mask, f, indent=2)

if __name__ == "__main__":
    main()