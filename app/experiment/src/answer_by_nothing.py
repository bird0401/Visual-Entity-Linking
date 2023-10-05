import json
from util import *

data_dir = "../../../data/clean"

def main():
    info = {"name": False, "article": False, "relations": False, "confidence": False}
    label = "nothing"

    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"

        with open(f"{category_dir}/qa_rephrase_mask.json") as f:
            qa_mask = json.load(f) 

        for entity_id in qa_mask:
            for i in range(len(qa_mask[entity_id])):
                qa_mask[entity_id][i]["A"+label] = answer(info, qa_mask[entity_id][i]["Q_rephrase_mask"])
                
        with open(f"{category_dir}/answers.json", 'w') as f:
            json.dump(qa_mask, f, indent=2)

if __name__ == "__main__":
    main()