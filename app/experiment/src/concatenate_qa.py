import json
import sys
sys.path.append("./utils")
from util import *

def concatenate_qa(category):
    print(f"category: {category}")
    data_dir = "../../../data/clean"
    category_dir = f"{data_dir}/{category}"
    patterns = [
        {"name": False, "article": False, "relations": False, "confidence": False}, 
        {"name": True, "article": False, "relations": False, "confidence": False}, 
        {"name": True, "article": True, "relations": False, "confidence": False}, 
        {"name": True, "article": False, "relations": True, "confidence": False}, 
        {"name": True, "article": True, "relations": True, "confidence": False}, 
        # {"name": True, "article": True, "relations": True, "confidence": True}, 
    ]

    # TODO: change by category
    # start_indice = [0] 
    # start_indice = [0, 5000, 10000] 
    start_indice = [0, 5000, 10000, 15000, 20000, 25000] 

    # TODO: change by category
    # pattern_mode = "all"
    pattern_mode = "split"

    # ans_mode = ""
    ans_mode = "oracle"
    # ans_mode = "oracle"

    keys = ["Q", "A", "Q_rephrase", "Q_rephrase_mask", "nothing", "name", "name_article", "name_relations", "name_article_relations"]
    keys_label = ["nothing", "name", "name_article", "name_relations", "name_article_relations"]

    qa_concatenate = {}
    for start_index in start_indice:
        print(f"start_index: {start_index}")
        if pattern_mode == "split":
            first_pattern = True
            for pattern in patterns:
                print(f"qas_{start_index}_{get_label(pattern)}.json")
                with open(f"{category_dir}/qas_{start_index}_{get_label(pattern)}_{ans_mode}.json") as f:
                    qas = json.load(f)
                for entity_id in qas:
                    for i, qa in enumerate(qas[entity_id]):
                        try:
                            if first_pattern:
                                if not entity_id in qa_concatenate:
                                    qa_concatenate[entity_id] = []
                                qa_concatenate[entity_id].append(qa)
                            else:
                                qa_concatenate[entity_id][i][get_label(pattern)] = qa[get_label(pattern)]
                        except:
                            print(f"qa: {qa}")
                            print(f"qa_concatenate[entity_id][i]: {qa_concatenate[entity_id][i]}")
                            # raise
                first_pattern = False
        elif pattern_mode == "all":
            print(f"qas_{start_index}.json")
            with open(f"{category_dir}/qas_{start_index}.json") as f:
                qas = json.load(f)
            for entity_id in qas:
                for i, qa in enumerate(qas[entity_id]):
                    if not entity_id in qa_concatenate:
                        qa_concatenate[entity_id] = []
                    qa_concatenate[entity_id].append(qa)


    # print(f"len(qa_concatenate): {len(qa_concatenate)}")
    total = 0
    remove_cnt = 0
    # print(f"qa_concatenate:")
    # print(qa_concatenate)

    # keysを全て含まないものは除外する
    for entity_id in list(qa_concatenate.keys()):
        remove_indices = []
        for i, qa in enumerate(qa_concatenate[entity_id]):
            total += 1
            if not all([key in qa for key in keys]):
                remove_indices.append(i)
                remove_cnt += 1
                continue
            # try:
            if not all([qa[key_label] and "A" in qa[key_label] and qa[key_label]["A"] for key_label in keys_label]):
                remove_indices.append(i)
                remove_cnt += 1
                continue
                # except:
                #     print(f"qa: {qa}")
                #     print(f"key: {key}")
                #     print(f"qa[key]: {qa[key]}")
                #     raise
        for i in remove_indices[::-1]:
            qa_concatenate[entity_id].pop(i)

        if len(qa_concatenate[entity_id]) == 0:
            qa_concatenate.pop(entity_id)

    print(f"len(qa_concatenate): {len(qa_concatenate)}")
    print(f"total: {total}")
    print(f"remove_cnt: {remove_cnt}\n")

    # qa_concatenateを保存する
    with open(f"{category_dir}/qas_concat.json", 'w') as f:
        json.dump(qa_concatenate, f, indent=2)

# 別々に出力した回答結果のファイルを結合
def main():
    # categories = ["director"]
    categories = ["us_politician"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "dog"]

    for category in categories:
        concatenate_qa(category)

if __name__ == '__main__':
    main()