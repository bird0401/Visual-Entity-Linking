import openai
import os, json
from util import *

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def merge_questions(qas):
    questions = []
    for qa in qas:
        questions.append(qa["Q"])
    questions_merge = "\n".join(questions)
    return questions_merge

def mask_entity_name(text, entity_name):
    MODEL = "gpt-3.5-turbo"
    messages=[
    {"role": "system", "content": "You are a helpful annotator of sentences."},
    {"role": "user", "content": f"Please convert '[MASK]' of following sentences to 'the athlete'. \n\nsentences:\n{text}\n\n"},
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
        with open(f"{category_dir}/qa_of_entities.json") as f:
            qa_of_entities = json.load(f)

        for entity_id in qa_of_entities:
            questions_merge = merge_questions(qa_of_entities[entity_id]["QA"])
            questions_masked = mask_entity_name(questions_merge, qa_of_entities[entity_id]["name"])
            questions_masked = questions_masked.split("\n")
            for i in range(len(qa_of_entities[entity_id]["QA"])):
                qa_of_entities[entity_id]["QA"][i]["Q_masked"] = questions_masked[i]
            
        with open(f"{category_dir}/qa_of_entities_masked.json", 'w') as f:
            json.dump(qa_of_entities, f, indent=2)

if __name__ == "__main__":
    main()

