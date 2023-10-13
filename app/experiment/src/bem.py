import json

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text

import numpy as np
from scipy.special import softmax

from utils.util import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def bertify_example(example):
    vocab_table = tf.lookup.StaticVocabularyTable(
            tf.lookup.TextFileInitializer(
                filename="../../../data/vocab.txt",
                key_dtype=tf.string,
                key_index=tf.lookup.TextFileIndex.WHOLE_LINE,
                value_dtype=tf.int64,
                value_index=tf.lookup.TextFileIndex.LINE_NUMBER
            ), 
            num_oov_buckets=1)
    cls_id, sep_id = vocab_table.lookup(tf.convert_to_tensor(['[CLS]', '[SEP]']))
    tokenizer = text.BertTokenizer(vocab_lookup_table=vocab_table, token_out_type=tf.int64, preserve_unused_token=True, lower_case=True)

    question = tokenizer.tokenize(example['question']).merge_dims(1, 2)
    reference = tokenizer.tokenize(example['reference']).merge_dims(1, 2)
    candidate = tokenizer.tokenize(example['candidate']).merge_dims(1, 2)
    input_ids, segment_ids = text.combine_segments((candidate, reference, question), cls_id, sep_id)

    return {'input_ids': input_ids.numpy(), 'segment_ids': segment_ids.numpy()}

def pad(a, length=512):
    return np.append(a, np.zeros(length - a.shape[-1], np.int32))

def bertify_examples(examples):
    input_ids = []
    segment_ids = []
    for example in examples:
        example_inputs = bertify_example(example)
        input_ids.append(pad(example_inputs['input_ids']))
        segment_ids.append(pad(example_inputs['segment_ids']))
    return {'input_ids': np.stack(input_ids), 'segment_ids': np.stack(segment_ids)}

def main():
    data_dir = "../../../data/clean"
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        logger.info(f"category: {category}")
        category_dir = f"{data_dir}/{category}"
        with open(f"{category_dir}/qas.json") as f:
            qas = json.load(f) 

        patterns = [
            {"name": False, "article": False, "relations": False, "confidence": False}, 
            {"name": True, "article": False, "relations": False, "confidence": False}, 
            {"name": True, "article": True, "relations": False, "confidence": False}, 
            {"name": True, "article": False, "relations": True, "confidence": False}, 
            {"name": True, "article": True, "relations": True, "confidence": False}, 
            # {"name": True, "article": True, "relations": True, "confidence": True}, 
        ]
        examples = []
        for entity_id in qas:
            for qa in qas[entity_id]:
                for info in patterns:
                    examples.append({
                        'question': qa['Q_rephrase'],
                        'reference': qa['A'],
                        'candidate': qa['A' + get_label(info)]
                        })
        inputs = bertify_examples(examples)

        bem = hub.load('https://tfhub.dev/google/answer_equivalence/bem/1')
        raw_outputs = bem(inputs) # The outputs are raw logits.
        bem_scores = softmax(np.squeeze(raw_outputs), axis=1)[:, 1]
        logger.info("bem_scores")
        for i in range(int(len(bem_scores) / len(patterns))):
            logger.info(bem_scores[i * len(patterns): (i + 1) * len(patterns)])

        j = 0
        for entity_id in qas:
            for qa in qas[entity_id]:
                for info in patterns:
                    qa['bem_score' + get_label(info)] = float(bem_scores[j])
                    j += 1
        logger.info(f"j: {j}")
        logger.info(f"len(be_scores): {len(bem_scores)}")
        
        with open(f"{category_dir}/qas_bem.json", 'w') as f:
            json.dump(qas, f, indent=2)

if __name__ == '__main__':
    main()