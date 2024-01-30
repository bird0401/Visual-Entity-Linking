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


vocab_table = tf.lookup.StaticVocabularyTable(
        tf.lookup.TextFileInitializer(
            filename=f"{data_dir}/vocab.txt",
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


# TODO: in this code, we truncate a if length of a is more than length
def pad(a, length=512):
    if length - a.shape[-1] < 0:
        print("length - a.shape[-1] < 0")
        return a[:, :length]
    return np.append(a, np.zeros(length - a.shape[-1], np.int32))


def bertify_examples(examples):
    input_ids = []
    segment_ids = []
    for example in examples:
        example_inputs = bertify_example(example)
        input_ids.append(pad(example_inputs['input_ids']))
        segment_ids.append(pad(example_inputs['segment_ids']))
    return {'input_ids': np.stack(input_ids), 'segment_ids': np.stack(segment_ids)}


def calculate_bem_score(qas, mode):
    examples = []
    # TODO: temporaly, execute in examples by qas per entity * the number od patterns = 10 * 5 = 50
    try: 
        for qa in qas:
            for pattern in patterns:
                pattern_label = get_label(pattern)
                examples.append({
                    'question': qa['Q_rephrase'],
                    'reference': qa['A'],
                    'candidate': qa[f"A_{mode}_{pattern_label}"]
                    })

        # for example in examples:
        #     print(example)
        # print(f"examples: {len(examples)}")
        
        inputs = bertify_examples(examples)
        # print(f"inputs: {len(inputs['input_ids'])}")

        raw_outputs = bem(inputs) # The outputs are raw logits.
        bem_scores = softmax(np.squeeze(raw_outputs), axis=1)[:, 1]
        # logger.info(f"len(be_scores): {len(bem_scores)}")
        logger.info("bem_scores")
        for i in range(int(len(bem_scores) / len(patterns))):
            logger.info(bem_scores[i * len(patterns): (i + 1) * len(patterns)])
    except Exception:
        traceback.print_exc()
        return
    
    # TODO: it is dangerous to assume that the index of qa is the same as the index of bem_scores
    # - if doing it, we should preprocess to delete empty qa
    # - or if make it expendable, we should implement it not depending on the index
    for i, qa in enumerate(qas):
        for j, pattern in enumerate(patterns):
            pattern_label = get_label(pattern)
            qa[f"A_{mode}_{pattern_label}_score"] = float(bem_scores[i * len(patterns) + j])


def calculate_bem_score_by_category(category, mode, start_idx, end_idx):
    # for category in categories:
    logger.info(f"category: {category}")

    entity_to_qas_path = get_entity_to_qas_path(category, start_idx, end_idx)
    with open(entity_to_qas_path) as f:
        entity_to_qas = json.load(f) 

    # batch_size = 10
    # TODO: currently, batch_size is executed in this code, but we should execute multiple times splitting by the batch_size
    # - batch_size may not be necessary because we execute by entity
    for i, entity_id in tqdm(enumerate(entity_to_qas)):
        logger.info(f"entity_id: {entity_id}")
        calculate_bem_score(entity_to_qas[entity_id], mode)

    entity_to_qas_bem_path = get_entity_to_qas_bem_path(category, start_idx, end_idx)
    with open(entity_to_qas_bem_path, 'w') as f:
        json.dump(entity_to_qas, f, indent=2)


# 注意: BERTを利用する際に、入力データが多いとセッションが切れる
# TODO: check the extent to which session is killed
def main():
    category = "aircraft"
    # category = sys.argv[1]
    # For test
    start_idx, end_idx = 0, 3
    # start_idx = int(sys.argv[1])
    # end_idx = int(sys.argv[2])
    mode = "oracle"
    # mode = sys.argv[3] # "oracle" or "pred"

    calculate_bem_score_by_category(category, mode, start_idx, end_idx)


if __name__ == '__main__':
    main()