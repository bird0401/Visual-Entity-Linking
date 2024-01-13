import json

data_dir = "../../../data"
def convert_label_to_id(category):
    category_dir = f"{data_dir}/{category}"
    with open(f"{category_dir}/map_id_to_label.json") as f:
        map_id_to_label = json.load(f)

    map_label_to_id = {}
    for id, label in map_id_to_label.items():
        map_label_to_id[str(label)] = id
    # with open(f"{category_dir}/map_label_to_id.json", 'w') as f:
    #     json.dump(map_label_to_id, f, indent=2)
    
    # TODO: MLの実行ごとにsave_dirは変更されるので、それに応じてここも変更する必要がある
    save_id = "0109-161637"
    save_dir = f"../weights/clean/{category}/{save_id}"
    with open(f"{save_dir}/id_indices_confidences_epoch10.json") as f:
        id_indices_confidences = json.load(f)
    
    # convert all labels to ids in id_indices_confidences_epoch10
    predicted_ids = {}
    for label, value in id_indices_confidences.items():
        wikidata_id = map_label_to_id[label]
        predicted_ids[wikidata_id] = {}
        predicted_ids[wikidata_id]["indices"] = [[map_label_to_id[str(label)] for label in indices_list] for indices_list in value["indices"]]
        predicted_ids[wikidata_id]["confidences"] = value["confidences"]

    with open(f"{save_dir}/predicted_ids.json", 'w') as f:
        json.dump(predicted_ids, f, indent=2)


def main():
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    categories = ["aircraft"]
    for category in categories:
        convert_label_to_id(category)


if __name__ == "__main__":
    main()