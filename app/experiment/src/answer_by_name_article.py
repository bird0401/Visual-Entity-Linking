import openai
import os, json, pickle
from util import *

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def answer_by_name_article(question, entity_name, article):
    messages=[
        {"role": "user", "content": f"Please answer the following question.\n\nEntity name: {entity_name}\nArticle:{article}\Question: {question}\n"},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    return response.choices[0]["message"]["content"]

# TODO: name of QA and answer file may mislead
def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"
        # Use this file for saving answers
        with open(f"{category_dir}/answers_by_name.json") as f:
            answers_by_name = json.load(f)
        with open(f"{category_dir}/id_to_name.pkl", 'rb') as f:
            id_to_name = pickle.load(f)

        for entity_id in answers_by_name:
            entity_name = id_to_name[entity_id]
            with open(f"{category_dir}/wikipedia/{entity_id}.txt") as f:
                article = f.read()
            if not article:
                print(f"Warning: {entity_id} has no text.")
                continue 
            input_text = customize_text(article)
            for i in range(len(answers_by_name[entity_id])):
                answers_by_name[entity_id][i]["A_by_name_article"] = answer_by_name_article(answers_by_name[entity_id][i]["Q_mask"], entity_name, input_text)
        
        with open(f"{category_dir}/answers_by_name_article.json", 'w') as f:
            json.dump(answers_by_name, f, indent=2)

if __name__ == "__main__":
    main()

