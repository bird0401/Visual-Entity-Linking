import openai
import os, json, pickle
from util import *

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def answer_by_name(question, entity_name):
    messages=[
        {"role": "user", "content": f"Please answer the following question.\n\nEntity name: {entity_name}\nQuestion: {question}\n"},
    ]
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
        # Use this file for saving answers
        with open(f"{category_dir}/qa_mask.json") as f:
            qa_mask = json.load(f) 
        with open(f"{category_dir}/id_to_name.pkl", 'rb') as f:
            id_to_name = pickle.load(f)

        for entity_id in qa_mask:
            entity_name = id_to_name[entity_id]
            for i in range(len(qa_mask[entity_id])):
                # answers.append(answer_by_entity_name(entity_name, qa["Q"]))
                qa_mask[entity_id][i]["A_by_name"] = answer_by_name(qa_mask[entity_id][i]["Q_mask"], entity_name)
                
        with open(f"{category_dir}/answers_by_name.json", 'w') as f:
            json.dump(qa_mask, f, indent=2)

if __name__ == "__main__":
    main()