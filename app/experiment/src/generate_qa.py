import openai
import os
import tiktoken
from util import *
import pandas as pd
import pickle

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def generate_qa(entity_name, article):
    messages = [
        {"role": "system", "content": "You are a helpful annotator of wikipedia articles."},
        {"role": "user", "content": f"Entity name: {entity_name}\nArticle:\n {input_text}\n\nGenerate five pairs of QA based on the article. Each question must contain the entity name. Use the following format:\nQ: Where was Thomas Flögel born?\nA: Vienna.\n\nQ: Which club did Thomas Flögel play for in Scotland?\nA: Heart of Midlothian.\n\nQ: How many league titles did Thomas Flögel win with Austria Wien?\nA: Three consecutive league titles.\n\nQ: Which club did Thomas Flögel return to after playing abroad?\nA: FK Austria.\n\nQ: What position did Thomas Flögel play during his time with Hearts?\nA: He played in every outfield position."},
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

        # with open(f"{category_dir}/csv/entity_ids_names.csv") as f:
        #     df = pd.read_csv(f)
        # print(len(df))

        with open(f"{category_dir}/id_to_name.pkl", 'rb') as f:
            id_to_name = pickle.load(f)

        output_dir = f"{category_dir}/gpt_3_output"
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        entity_text_files = os.listdir(f"{category_dir}/wikipedia")
        for entity_text_file in entity_text_files:
            entity_id = entity_text_file.split(".")[0]
            entity_name = id_to_name[entity_id]
            with open(f"{category_dir}/wikipedia/{entity_text_file}") as f:
                article = f.read()
            if not article:
                print(f"Warning: {entity_id} has no text.")
                print("remove the file")
                os.remove(f"{category_dir}/wikipedia/{entity_id}.txt")
                continue 
            input_text = customize_text(article)
            output = generate_qa(entity_name, input_text)
            if output:
                with open(f"{output_dir}/{entity_text_file}", 'w') as f:
                    f.write(output)
            else:
                print(f"Warning: {entity_id} has no output.")

if __name__ == "__main__":
    main()

