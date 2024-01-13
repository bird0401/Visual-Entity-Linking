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

# decide maxlength her

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

bem = hub.load('https://tfhub.dev/google/answer_equivalence/bem/1')


def bertify_example(example):
    question = tokenizer.tokenize(example['question']).merge_dims(1, 2)
    reference = tokenizer.tokenize(example['reference']).merge_dims(1, 2)
    candidate = tokenizer.tokenize(example['candidate']).merge_dims(1, 2)

    # 長さを超過するとpadでエラーになるのでtruncateする。input_idsの長さは512以下にする必要がある。
    if question.numpy().shape[-1] > 150:
        question = question[:, :150]
    if reference.numpy().shape[-1] > 150:
        reference = reference[:, :150]
    if candidate.numpy().shape[-1] > 150:
        candidate = candidate[:, :150]

    input_ids, segment_ids = text.combine_segments((candidate, reference, question), cls_id, sep_id)

    # 長さを超過するとpadでエラーになるのでtruncateする
    if input_ids.numpy().shape[-1] > 512:
        input_ids = input_ids[:, :512]

    return {'input_ids': input_ids.numpy(), 'segment_ids': segment_ids.numpy()}

def pad(a, length=512):
    if length - a.shape[-1] < 0:
        print("length - a.shape[-1] < 0")
        return a[:, :length]
    # try:
    return np.append(a, np.zeros(length - a.shape[-1], np.int32))
    # except:
    #     print(f"length - a.shape[-1]: {length} - {a.shape[-1]}")
    #     print(f"a.shape: {a.shape}")
    #     raise

def bertify_examples(examples):
    input_ids = []
    segment_ids = []
    for example in examples:
        example_inputs = bertify_example(example)
        input_ids.append(pad(example_inputs['input_ids']))
        segment_ids.append(pad(example_inputs['segment_ids']))
    return {'input_ids': np.stack(input_ids), 'segment_ids': np.stack(segment_ids)}

# TODO: 10ずつログ出力するようにする
# 注意: BERTを利用する際に、入力データが多いとセッションが切れる
def main():
    data_dir = "../../../data/clean"
    # categories = ["aircraft"]
    # start_index = 0
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "dog"]
    categories = [sys.argv[1]]

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


        entity_ids = list(qas.keys())
        # interval = 10
        # for start in range(0, len(entity_ids), interval):
            # logger.info(f"start/len(entity_ids): {start}/{len(entity_ids)}")
            # for entity_id in entity_ids[start:start+interval]:
        for pattern in patterns:
            logger.info(f"pattern: {get_label(pattern)}\n")
            total = 0
            correct = 0
            # for start in range(0, len(entity_ids), interval):
            # for start in range(0, 10, interval): # セッションが切れてしまうため、ここで10で打ち止め
                # logger.info(f"start/len(entity_ids): {start}/{len(entity_ids)}")
                # for entity_id in entity_ids[start:start+interval]:
            for i, entity_id in enumerate(entity_ids[:100]):
                if i % 10 == 0:
                    logger.info(f"i/len(entity_ids): {i}/{len(entity_ids)}")
                    logger.info(f"correct/total: {correct}/{total} = {correct / total if total > 0 else 0}")
                    print()
            # for i, entity_id in enumerate(entity_ids):
            #     if i % 100 == 0:
                    # logger.info(f"i/len(entity_ids): {i}/{len(entity_ids)}")
                    # with open(f"{category_dir}/qas_bem_{i}.json", 'w') as f:
                    #     json.dump(qas, f, indent=2)
                
                examples = []
                for qa in qas[entity_id]:
                # for key in ['A', 'Q_rephrase']:
                    # if not key in qa or not qa[key]:
                    #     logger.info(f"no {key}: {qa}")
                    #     continue
                
                    # if not get_label(pattern) in qa or not 'A' in qa[get_label(pattern)] or not qa[get_label(pattern)]['A']:
                    #     logger.info(f"no answer: {qa}")
                    #     continue
                    try:
                        examples.append({
                            'question': qa['Q_rephrase'],
                            'reference': qa['A'],
                            'candidate': qa[get_label(pattern)]['A']
                            })
                    except:
                        logger.info(f"qa: {qa}")
                        logger.info(f"pattern: {pattern}")
                        raise
        
                # for example in examples:
                #     print(example)
                # print(f"examples: {len(examples)}")
                inputs = bertify_examples(examples)
                # print(f"inputs: {len(inputs['input_ids'])}")

                
                raw_outputs = bem(inputs) # The outputs are raw logits.
                bem_scores = softmax(np.squeeze(raw_outputs), axis=1)[:, 1]
                # logger.info("bem_scores")
                # for i in range(int(len(bem_scores) / len(patterns))):
                #     logger.info(bem_scores[i * len(patterns): (i + 1) * len(patterns)])

                # for entity_id in qas[start:start+100]:
                # for entity_id in entity_ids[start:start+interval]:

                for bem_score in bem_scores:
                    if bem_score >= 0.5:
                        correct += 1
                    total += 1

                logger.info(f"i/len(entity_ids): {i}/{len(entity_ids)}")
                logger.info(f"correct/total: {correct}/{total} = {correct / total if total > 0 else 0}")
                print()

                # for j, qa in enumerate(qas[entity_id]):
                #     for info in patterns:
                #         if not get_label(info) in qa:
                #             continue
                #         qa[get_label(info)]['bem_score'] = float(bem_scores[j])

                # logger.info(f"len(be_scores): {len(bem_scores)}")
    
        # with open(f"{category_dir}/qas_bem.json", 'w') as f:
        #     json.dump(qas, f, indent=2)

if __name__ == '__main__':
    main()