import openai
import os
import tiktoken
from util import *
import pandas as pd

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def generate_qa(entity_id, entity_name, category_dir):
    print(f"entity_id: {entity_id}, entity_name: {entity_name}")

    input_text = fetch_text(entity_id, category_dir)

    messages = [
        {"role": "system", "content": "You are a helpful annotator of wikipedia articles."},
        {"role": "user", "content": f"Please generate 5 pairs of QA based on the part of article. ALL questions must contain a word that serves as the entity name.\n\nUse the following format:\nQ: What is the origin of the {entity_name}?\nA: Mexico.\n\nQ: What is the percentage of {entity_name} that have hair?\nA: Approximately 97% of Chihuahuas have hair.\n\nEntity name of following article: {entity_name}\nArticle:\n {input_text}"},
    ]
    print(messages[1]["content"])

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

        with open(f"{category_dir}/csv/entity_ids_names.csv") as f:
            df = pd.read_csv(f)

        print(f"len(df): {len(df)}")

        output_dir = f"{category_dir}/gpt_3_output"

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        
        for entity_id, entity_name in zip(df["wikidata_id"], df["entity_name"]):
            output = generate_qa(entity_id, entity_name, category_dir)
            if output:
                with open(f"{output_dir}/{entity_id}.txt", 'w') as f:
                    f.write(output)

if __name__ == "__main__":
    main()

