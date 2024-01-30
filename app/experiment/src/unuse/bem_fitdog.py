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

import sys


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
    if length - a.shape[-1] < 0:
        print("length - a.shape[-1] < 0")
        return None
    # try:
    return 1
    # return np.append(a, np.zeros(length - a.shape[-1], np.int32))
    # except:
    #     print(f"length - a.shape[-1]: {length} - {a.shape[-1]}")
    #     print(f"a.shape: {a.shape}")
    #     raise

# def bertify_examples(examples):
#     input_ids = []
#     segment_ids = []
#     unfit_ids = []
#     for i, example in enumerate(examples):
#         example_inputs = bertify_example(example)
#         input_id = pad(example_inputs['input_ids'])
#         if input_id is None:
#             unfit_ids.append(i)
#         # input_ids.append(pad(example_inputs['input_ids']))
#         # segment_ids.append(pad(example_inputs['segment_ids']))
#     # return {'input_ids': np.stack(input_ids), 'segment_ids': np.stack(segment_ids)}
#     return unfit_ids

def main():
    data_dir = "../../../data/clean"
    categories = ["dog"]
    # start_index = 0
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "dog"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        logger.info(f"category: {category}")
        category_dir = f"{data_dir}/{category}"
        with open(f"{category_dir}/qas_concat.json") as f:
            qas = json.load(f) 
        # execute all patterns at the same time
        patterns = [
            {"name": False, "article": False, "relations": False, "confidence": False}, 
            {"name": True, "article": False, "relations": False, "confidence": False}, 
            {"name": True, "article": True, "relations": False, "confidence": False}, 
            {"name": True, "article": False, "relations": True, "confidence": False}, 
            {"name": True, "article": True, "relations": True, "confidence": False}, 
            # {"name": True, "article": True, "relations": True, "confidence": True}, 
        ]
        # pattern_mode = int(sys.argv[1])
        # pattern = patterns[pattern_mode]

        entity_ids = list(qas.keys())
        for i, entity_id in enumerate(entity_ids):
            if i % 100 == 0:
                logger.info(f"{i}/{len(entity_ids)}")
            unfit_indices = []
            for i, qa in enumerate(qas[entity_id]):
                for j, pattern in enumerate(patterns):
                    example = {
                        'question': qa['Q_rephrase'],
                        'reference': qa['A'],
                        'candidate': qa[get_label(pattern)]['A']
                        }
                    example_inputs = bertify_example(example)
                    input_id = pad(example_inputs['input_ids'])
                    # 1つでもNoneがあれば、そのiは不適切なので、iを記録しておく
                    if input_id is None:
                        unfit_indices.append(i)
                        print(f"remove unfit example")
                        break
            for k in unfit_indices[::-1]:
                qas[entity_id].pop(k)

        print(f"len(qas): {len(qas)}")
        print(f"{category_dir}/qas_concat_fit{pattern}.json)")
        with open(f"{category_dir}/qas_concat_fit{pattern}.json", 'w') as f:
            json.dump(qas, f, indent=2)


if __name__ == '__main__':
    main()