# 実際のMLモデルの出力に基づいて基づいて作成するため、不要となった。

import os
import random
import json


def generate_predicted_ids(category):
    print(f"category: {category}")
    data_dir = "../../../data/clean"
    category_dir = f"{data_dir}/{category}"
    # ids = os.listdir(f"{category_dir}/images")

    # TODO: id_to_nameで代用しているが、本来はqaを利用するべき
    with open(f"{category_dir}/id_to_name.json") as f:
        id_to_name = json.load(f)
    ids = list(id_to_name.keys())
    # ids = ids[:10] # for testing
    # print(ids[:20])

    # randomly generate correct or incorrect
    correct = {}
    # Generate a random boolean list
    # true_ratio = random.uniform(0.2, 0.8)  # change by category
    category_to_true_ratio = {
        "aircraft": 0.505,
        "athlete": 0.504,
        "bird": 0.742,
        "bread": 0.430,
        "car": 0.718,
        "director": 0.560,
        "dog": 0.661,
        "us_politician": 0.522,
    }
    true_ratio = category_to_true_ratio[category]
    print(f"true_ratio: {true_ratio}")
    bool_list = random.choices([True, False], weights=[true_ratio, 1 - true_ratio], k=len(ids))
    for i in range(len(ids)):
        correct[ids[i]] = bool_list[i]
    # print("correct")
    # print(correct)

    predicted_ids = {}
    for id in ids:
        if correct[id]:
            predicted_ids[id] = id
        else:
            while True:
                choice_id = random.choice(ids)
                if choice_id != id:
                    break
            predicted_ids[id] = choice_id
    # print("predicted_ids")
    # print(predicted_ids)
    print(f"len(predicted_ids): {len(predicted_ids)}")
    with open(f"{category_dir}/predicted_ids.json", 'w') as f:
        json.dump(predicted_ids, f, indent=2)


def main():
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # categories = ["aircraft"]
    for category in categories:
        generate_predicted_ids(category)


if __name__ == "__main__":
    main()




#    アメリカの政治家 & 0.330 & 0.220 & 0.522 & 0.438\\
#    ディレクター & 0.426 & 0.291 & 0.560 & 0.442\\
#    アスリート & 0.780 & 0.747 & 0.969 & 0.961\\
#    犬 & 0.581 & 0.435 & 0.661 & 0.527\\
#    鳥 & 0.747 & 0.671 & 0.742 & 0.687\\
#    パン & 0.413 & 0.225 & 0.430 & 0.285\\
#    車 & 0.662 & 0.505 & 0.718 & 0.551\\
#    飛行機 & 0.429 & 0.218 & 0.505 & 0.296\\