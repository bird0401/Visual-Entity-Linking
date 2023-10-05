import openai
import os, json, pickle, textwrap
from util import *

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def rephrase_questions(text):
    prompt = f"""
                In this task, please paraphrase sentences. See the examples below.

                Before paraphrasing:
                When was Azzeddine Toufiqui born?
                Which position does Azzeddine Toufiqui play in football?
                Which club did Azzeddine Toufiqui join in 2015?
                In which league did Azzeddine Toufiqui's former club Caen play?
                When did Azzeddine Toufiqui make his professional debut?

                After paraphrasing:
                What is the birth date of Azzeddine Toufiqui?
                What is Azzeddine Toufiqui's football position?
                In 2015, which team did Azzeddine Toufiqui become a member of?
                Which league did Caen, Azzeddine Toufiqui's previous club, compete in?
                When did Azzeddine Toufiqui first play professionally?

                Based on the above examples, please paraphrase following sentences:
                """
    prompt_dedent = textwrap.dedent(prompt)
    messages=[
        {"role": "system", "content": "You are a helpful annotator of sentences."},
        {"role": "user", "content": f"{prompt_dedent}\n{text}"},
    ]
    # print(messages[1]["content"])
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    # print("response:")
    # print(response.choices[0]["message"]["content"])
    return response.choices[0]["message"]["content"]

def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"
        with open(f"{category_dir}/qa.json") as f:
            qa_of_entities = json.load(f)
        for entity_id in qa_of_entities:
            questions_merge = merge_text(qa_of_entities[entity_id], "Q")
            questions_rephrased = rephrase_questions(questions_merge)
            questions_rephrased_list = questions_rephrased.split("\n")
            for i in range(len(qa_of_entities[entity_id])):
                qa_of_entities[entity_id][i]["Q_rephrase"] = questions_rephrased_list[i]
        with open(f"{category_dir}/qa_rephrase.json", 'w') as f:
            json.dump(qa_of_entities, f, indent=2)

if __name__ == "__main__":
    main()

