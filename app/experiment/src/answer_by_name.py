import openai
import os, json
from util import *

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def answer_by_name(entity_name, question):
    MODEL = "gpt-3.5-turbo"
    messages=[
        {"role": "user", "content": f"Please answer the following question.\n\nEntity name: {entity_name}\nQuestion: {question}\n"},
    ]

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0,
    )
    return response.choices[0]["message"]["content"]

def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"
        with open(f"{category_dir}/qa_of_entities_masked.json") as f:
            qa_of_entities_masked = json.load(f)

        answers_by_id = {}
        for entity_id in qa_of_entities_masked:
            entity_name = qa_of_entities_masked[entity_id]["name"]
            answers = []
            for qa in qa_of_entities_masked[entity_id]["QA"]:
                # answers.append(answer_by_entity_name(entity_name, qa["Q"]))
                answers.append(answer_by_name(entity_name, qa["Q_masked"]))
            answers_by_id[entity_id] = answers
        
        with open(f"{category_dir}/answers_by_name.json", 'w') as f:
            json.dump(answers_by_id, f, indent=2)

if __name__ == "__main__":
    main()

