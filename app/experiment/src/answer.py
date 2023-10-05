import json, pickle
from util import *

# openai.organization = os.getenv("OPENAI_ORGANIZATION")
# openai.api_key = os.getenv("OPENAI_API_KEY")
data_dir = "../../../data/clean"

def answer(info, question, category="", entity_name="", article="", text_by_relation=""):
    messages = []
    if info["name"]:
        messages.append({"role": "system", "content": f"Name of the {category}: {entity_name}\n"})
    if info["article"]:
        messages.append({"role": "system", "content": f"Article:\n{article}\n"})
    if info["relations"]:
        messages.append({"role": "system", "content": f"Relations:\n{text_by_relation}\n"})
    messages.append({"role": "user", "content": f"Please answer the following question.\nQuestion: {question}\n"})
    for message in messages:
        print(message["content"])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )

    return response.choices[0]["message"]["content"]

def get_label(info):
    if not any(info.values()):
        label = "_nothing"
    else:
        label = ""
        for key in info:
            if info[key]:
                label += "_" + key
    return label

# TODO: name of QA and answer file may mislead
def main():
    # info = {"name": False, "article": False, "relations": False, "confidence": False} 
    # info = {"name": True, "article": False, "relations": False, "confidence": False} 
    # info = {"name": True, "article": True, "relations": False, "confidence": False} 
    # info = {"name": True, "article": False, "relations": True, "confidence": False} 
    info = {"name": True, "article": True, "relations": True, "confidence": False} 
    # info = {"name": True, "article": True, "relations": True, "confidence": True} 
    label = get_label(info)

    entity_name, input_text, text_by_relation = "", "", ""
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        category_dir = f"{data_dir}/{category}"

        with open(f"{category_dir}/qa_rephrase_mask.json") as f:
            qa_mask = json.load(f) 
        if info["name"]:
            with open(f"{category_dir}/id_to_name.pkl", 'rb') as f:
                id_to_name = pickle.load(f)
        if info["relations"]:
            with open(f"{category_dir}/id_to_text_by_relation.json") as f:
                id_to_text_by_relation = json.load(f)

        for entity_id in qa_mask:
            if info["name"]:
                entity_name = id_to_name[entity_id]
            if info["article"]:
                with open(f"{category_dir}/wikipedia/{entity_id}.txt") as f:
                    article = f.read()
                input_text = customize_text(article)
            if info["relations"]:
                text_by_relation = id_to_text_by_relation[entity_id]
            for i in range(len(qa_mask[entity_id])):
                qa_mask[entity_id][i]["A"+label] = answer(info, qa_mask[entity_id][i]["Q_rephrase_mask"], category, entity_name, input_text, text_by_relation)

        with open(f"{category_dir}/qa_rephrase_mask.json", 'w') as f:
            json.dump(qa_mask, f, indent=2)

if __name__ == "__main__":
    main()