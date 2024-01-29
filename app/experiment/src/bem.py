import json

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text

import numpy as np
from scipy.special import softmax

from tqdm import tqdm

from util import *
from config import *

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


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
# TODO: check the extent to which session is killed
def main():
    # categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # categories = [sys.argv[1]]
    category = "aircraft"
    # For test
    start_idx, end_idx = 0, 3
    # start_idx = int(sys.argv[1])
    # end_idx = int(sys.argv[2])
    ans_mode = "oracle"

    # for category in categories:
    logger.info(f"category: {category}")

    entity_to_qas_path = get_entity_to_qas_path(category, start_idx, end_idx)
    with open(entity_to_qas_path) as f:
        entity_to_qas = json.load(f) 

    total = 0
    correct = 0
    batch_size = 10
    # TODO: currently, batch_size is executed in this code, but we should execute multiple times splitting by the batch_size
    # - batch_size may not be necessary because we execute by entity
    for i, (entity_id, qas) in tqdm(enumerate(entity_to_qas[0:batch_size].items())):
        logger.info(f"entity_id: {entity_id}, correct/total: {correct}/{total} = {correct / total if total > 0 else 0}")
        
        try:
            examples = []
            # TODO: temporaly, execute in examples by qas per entity * the number od patterns = 10 * 5 = 50
            for qa in qas:
                for pattern in patterns:
                    pattern_label = get_label(pattern)
                    # logger.info(f"pattern: {pattern_label}")
                    # if not qa['Q_rephrase'] or not qa['A'] or not qa[f"A_{pattern_label}_{ans_mode}"]:
                    #     logger.info(f"Sentence is empty: {qa}")
                    examples.append({
                        'question': qa['Q_rephrase'],
                        'reference': qa['A'],
                        'candidate': qa[f"A_{pattern_label}_{ans_mode}"]
                        })

                # for example in examples:
                #     print(example)
                print(f"examples: {len(examples)}")
                
                inputs = bertify_examples(examples)
                print(f"inputs: {len(inputs['input_ids'])}")

                raw_outputs = bem(inputs) # The outputs are raw logits.
                bem_scores = softmax(np.squeeze(raw_outputs), axis=1)[:, 1]
                logger.info(f"len(be_scores): {len(bem_scores)}")
                logger.info("bem_scores")
                for i in range(int(len(bem_scores) / len(patterns))):
                    logger.info(bem_scores[i * len(patterns): (i + 1) * len(patterns)])

        except:
            logger.info(f"entity_id: {entity_id}")
            traceback.print_exc()
            continue
    
        # for testing the extent to which the correct answers are 
        for bem_score in bem_scores:
            if bem_score >= 0.5:
                correct += 1
            total += 1

        # TODO: it is dangerous to assume that the index of qa is the same as the index of bem_scores
        # - if doing it, we should preprocess to delete empty qa
        # - or if make it expendable, we should implement it not depending on the index
        for i, qa in enumerate(qas):
            for j, pattern in enumerate(patterns):
                pattern_label = get_label(pattern)
                qa[f"A_{pattern_label}_{ans_mode}_score"] = float(bem_scores[i * len(patterns) + j])

    # TODO: temporary file name 
    with open(f"bem_{entity_to_qas_path}", 'w') as f:
        json.dump(qas, f, indent=2)


if __name__ == '__main__':
    main()