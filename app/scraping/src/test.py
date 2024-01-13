import json
import os
import traceback

def test(category):
    # data_dir = f"../../../data/clean"
    # category_dir = f"{data_dir}/{category}"
    # with open(f'{category_dir}/wikidata_with_commons.json') as f:
    #     ids_file = json.load(f)
    # ids = list(ids_file.keys())
    # print(f"len(ids): {len(ids)}")
    # print(ids.index("Q8006310"))
    # for id in ids[:10]: # テスト用
    # 取得元のファイルは変えず、そのどのidから収集するかのみを変更する

    print(category)
    category_dir = f"../../../data/clean/{category}"
    with open(f'{category_dir}/wikidata_filtered.json') as f:
        wikidata = json.load(f)
    ids = list(wikidata.keys())
    print(f"len(wikidata): {len(wikidata)}")
    print(ids.index("Q698851"))

    # # # 画像枚数確認用
    # category_image_dir = f"{category_dir}/images"
    # dir_names = os.listdir(category_image_dir)
    # print(f"len(dir_names): {len(dir_names)}")
    # cnt = 0
    # for dir_name in dir_names:
    #     if dir_name in wikidata:
    #         cnt += 1
    # print(f"cnt: {cnt}")

    try:
        qas_file = f"{category_dir}/qas_0.json"
        with open(qas_file) as f:
            qas = json.load(f)
        print(f"len(qas): {len(qas)}")
        cnts = {"nothing": 0, "name": 0, "name_article": 0, "name_relations": 0, "name_article_relations": 0}
        # cnts = {"Q": 0, "A": 0, "Q_rephrase": 0, "Q_rephrase_mask": 0}
        for id in qas:
            for i, qa in enumerate(qas[id]):
                for key in cnts:
                    if key not in qa:
                        cnts[key] += 1
                        # print(f"id[i]: {id}[{i}]")
                        # print(f"{key}: {qa}")

        print(cnts)
    except:
        traceback.print_exc()

def main():
    categories = ["director"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "dog"]
    for category in categories:
        test(category)

if __name__ == "__main__":
    main()