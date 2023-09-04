import openai
import os
import tiktoken
from util import *
import pandas as pd

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def generate_qa(entity_id, entity_name):
    print(f"entity_id, entity_name: {entity_id}, {entity_name}")

    with open(f"{data_dir}/wikipedia/{entity_id}.txt") as f:
        text = f.read()
    clean_text = text.replace("  ", " ").replace("\n", "; ").replace(';',' ')

    template_messages = [
        {"role": "system", "content": "You are a helpful annotator of wikipedia articles."},
        {"role": "user", "content": f"Please generate 5 pairs of QA based on the article. ALL questions must contain a word that serves as the entity name.\n\nUse the following format:\nQ: What is the origin of the {entity_name}?\nA: Mexico.\n\nQ: What is the percentage of {entity_name} that have hair?\nA: Approximately 97% of Chihuahuas have hair.\n\n"},
    ]
    template_content = f"Entity name of following article: {entity_name}\nArticle:\n <document>"

    tokenizer = tiktoken.get_encoding("cl100k_base")
    chunks = create_chunks(clean_text,4000,tokenizer)
    text_chunks = [tokenizer.decode(chunk) for chunk in chunks]
    results = []
    MODEL = "gpt-3.5-turbo"

    for chunk in text_chunks:
        results.append(extract_chunk(chunk, template_messages, template_content, MODEL))

    output = ""
    for result in results:
        output += result + "\n\n"
    output = output.rstrip()
    print(output)
    print()

    if not os.path.exists(f"{data_dir}/gpt_3_output"):
        os.mkdir(f"{data_dir}/gpt_3_output")
        
    with open(f"{data_dir}/gpt_3_output/{entity_id}.txt", 'w') as f:
        f.write(output)

def main():
    with open(f"{data_dir}/entity.csv") as f:
        df = pd.read_csv(f)
    for entity_id, entity_name in zip(df["id"], df["name"]):
        generate_qa(entity_id, entity_name)

if __name__ == "__main__":
    main()

