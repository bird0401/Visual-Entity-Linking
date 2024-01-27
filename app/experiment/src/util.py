import tiktoken

import json
import traceback

import logging
import logging.config
from yaml import safe_load

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
) 

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")

def get_label(info):
    if not any(info.values()):
        return "nothing"
    else:
        return "_".join([key for key in info if info[key]])
        # label = ""
        # for key in info:
            # if info[key]:
            #     label += "_" + key
    return label

def merge_text(qas, key):
    questions = []
    for qa in qas:
        questions.append(qa[key])
    questions_text = "\n".join(questions)
    return questions_text

def customize_text_for_gpt_3_5(article):  
    article = article.strip()
    clean_article = article.replace("  ", " ").replace("\n", "; ").replace(';',' ')
    tokenizer = tiktoken.get_encoding("cl100k_base")
    input_text = tokenizer.decode(tokenizer.encode(clean_article)[:4096-1000])
    return input_text

def customize_relations(relations):  
    relations = relations.strip()
    clean_relations = relations.replace("  ", " ").replace("\n", "; ").replace(';',' ')
    tokenizer = tiktoken.get_encoding("cl100k_base")
    input_text = tokenizer.decode(tokenizer.encode(clean_relations)[:500])
    return input_text

# Split a text into smaller chunks of size n, preferably ending at the end of a sentence
# NOT USE NOW
def create_chunks(text, n, tokenizer):
    tokens = tokenizer.encode(text)
    """Yield successive n-sized chunks from text."""
    i = 0
    while i < len(tokens):
        # Find the nearest end of sentence within a range of 0.5 * n and 1.5 * n tokens
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith(".") or chunk.endswith("\n"):
                break
            j -= 1
        # If no end of sentence found, use n tokens as the chunk size
        if j == i + int(0.5 * n):
            j = min(i + n, len(tokens))
        yield tokens[i:j]
        i = j

# NOT USE NOW
def cut_text(text, n, tokenizer):
    tokens = tokenizer.encode(text)
    i = 0
    while i < len(tokens):
        # Find the nearest end of sentence within a range of 0.5 * n and 1.5 * n tokens
        j = min(n, len(tokens))
        while j > i:
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith("."):
                break
            j -= 1
        logger.info(f"len(tokens[i:j]): {len(tokens[i:j])}")
        return tokenizer.decode(tokens[i:j])

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.info("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        logger.info("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        logger.info("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens



def bem_score_to_bool(bem_score):
    # We assume that the threshold is 0.5
    if bem_score >= 0.5:
        return 1
    else:
        return 0

def generate_booled_qas(qas):
    for entity_id in qas:
        for qa in qas[entity_id]:
            qa["bem_score_bool"] = bem_score_to_bool(qa["bem_score"])
    return qas

def output_booled_qa(category_dir):
    with open(f"{category_dir}/qas.json") as f:
        qas = json.load(f) 
    booled_qas = generate_booled_qas(qas)
    with open(f"{category_dir}/qas_bool.json", 'w') as f:
        json.dump(booled_qas, f, indent=2)

def calculate_accuracy(qas_bem_path, pattern):
    with open(qas_bem_path) as f:
        qas_bem = json.load(f) 
    total = 0
    correct = 0
    for entity_id in qas_bem:
        for qa in qas_bem[entity_id]:
            if qa[get_label(pattern)]["bem_score"] >= 0.5:
                correct += 1
            total += 1
    return correct / total


@retry(
    retry=retry_if_exception_type((openai.error.APIError, openai.error.APIConnectionError, openai.error.RateLimitError, openai.error.ServiceUnavailableError, openai.error.Timeout)), 
    wait=wait_random_exponential(min=1, max=60), 
    stop=stop_after_attempt(6), 
)
def gpt_request(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
        )
        return response.choices[0]["message"]["content"]
    except Exception:
        print(f"messages")
        print(messages)
        traceback.print_exc()