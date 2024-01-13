import json
import os
import traceback

def cnt_images(category):
    category_dir = f"../../../data/clean/{category}"
    with open(f'{category_dir}/wikidata_with_commons.json') as f:
        wikidata = json.load(f)
    category_image_dir = f"{category_dir}/images"
    dir_names = os.listdir(category_image_dir)
    cnt = 0
    image_files_cnt = 0
    for dir_name in dir_names:
        if dir_name in wikidata:
            cnt += 1
            image_files_cnt += len(os.listdir(f"{category_image_dir}/{dir_name}"))
    return cnt, image_files_cnt

def cnt_qas(category):
    category_dir = f"../../../data/clean/{category}"
    qas_file = f"{category_dir}/qas_0.json"
    with open(qas_file) as f:
        qas = json.load(f)
    qa_cnt = 0
    for id in qas:
        qa_cnt += len(qas[id])
    return len(qas), qa_cnt

def cnt_relations(category):
    category_dir = f"../../../data/clean/{category}"
    with open(f'{category_dir}/wikidata_filtered.json') as f:
        wikidata = json.load(f)
    relation_cnt = 0
    relations = set()
    for id in wikidata:
        relation_cnt += len(wikidata[id]["relations"])
        for relation in wikidata[id]["relations"]:
            relations.add(relation)
    print(f"len(wikidata): {len(wikidata)}")
    print(f"relation_cnt: {relation_cnt}")
    print(f"relation_cnt/len(wikidata): {relation_cnt/len(wikidata)}")
    print(f"len(relations): {len(relations)}\n")
    # print(relations)
    return relation_cnt, len(wikidata), relations

def test(category):
    print(category)
    category_dir = f"../../../data/clean/{category}"
    with open(f'{category_dir}/wikidata_filtered.json') as f:
        wikidata = json.load(f)
    
    # 画像収集進捗確認用
    # ids = list(wikidata.keys())
    # print(f"len(wikidata): {len(wikidata)}")
    # print(ids.index("Q698851"))

    # QA数確認用
    try:
        qas_file = f"{category_dir}/qas_0.json"
        with open(qas_file) as f:
            qas = json.load(f)
        print(f"len(qas): {len(qas)}")
        qa_cnt = 0
        # cnts = {"nothing": 0, "name": 0, "name_article": 0, "name_relations": 0, "name_article_relations": 0}
        # cnts = {"Q": 0, "A": 0, "Q_rephrase": 0, "Q_rephrase_mask": 0}
        for id in qas:
            qa_cnt += len(qas[id])
            # for i, qa in enumerate(qas[id]):
                # for key in cnts:
                #     if key not in qa:
                #         cnts[key] += 1
                        # print(f"id[i]: {id}[{i}]")
                        # print(f"{key}: {qa}")

        # print(cnts)
        print(f"qa_cnt: {qa_cnt}")
        print(f"qa_cnt / len(qas): {qa_cnt / len(qas)}\n")
        return len(qas), qa_cnt
    except:
        traceback.print_exc()

def main():
    # categories = ["director"]
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "dog"]
    total_cnt = 0
    total_image_files_cnt = 0
    total_len_qa = 0
    total_qa_cnt = 0
    total_relation_cnt = 0
    entity_cnt = 0
    total_relatinos = set()
    for category in categories:
        print(category)

        # len_qa, qa_cnt = cnt_qas(category)
        # total_len_qa += len_qa
        # total_qa_cnt += qa_cnt

        # cnt, image_files_cnt  = cnt_images(category)
        # total_cnt += cnt
        # total_image_files_cnt += image_files_cnt

        relation_cnt, len_wikidata, relations = cnt_relations(category)
        total_relation_cnt += relation_cnt
        entity_cnt += len_wikidata
        total_relatinos |= relations
    
    # print(f"total_cnt: {total_cnt}")
    # print(f"total_image_files_cnt: {total_image_files_cnt}")
    # print(f"total_image_files_cnt / total_cnt: {total_image_files_cnt / total_cnt}")

    # print(f"total_qa_cnt: {total_qa_cnt}")
    # print(f"total_qa_cnt / len_qa: {total_qa_cnt / total_len_qa}")
        
    print(f"total_relation_cnt: {total_relation_cnt}")
    print(f"entity_cnt: {entity_cnt}")
    print(f"total_relation_cnt / entity_cnt: {total_relation_cnt / entity_cnt}")
    print(f"len(total_relatinos): {len(total_relatinos)}")


if __name__ == "__main__":
    main()