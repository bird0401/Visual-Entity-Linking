import sys
import json
from util import *
from config import *


def calculate_accuracy(entity_to_qas_bem_path, pattern, mode):
    with open(entity_to_qas_bem_path) as f:
        entity_to_qas_bem = json.load(f) 
    pattern_label = get_label(pattern)

    total = 0
    correct = 0
    for entity_id, qas in entity_to_qas_bem.items():
        for qa in qas:
            if qa[f"A_{mode}_{pattern_label}_score"]["bem_score"] >= 0.5:
                correct += 1
            total += 1
    return correct / total


def main():
    # categories = [sys.argv[1]]
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    start_idx, end_idx = 0, 3
    mode = "oracle"

    for category in categories:
        entity_to_qas_bem_path = get_entity_to_qas_bem_path(category, start_idx, end_idx)
        for pattern in patterns:
            accuracy = calculate_accuracy(entity_to_qas_bem_path, pattern, mode)
            print(f"category: {category}")
            print(f"pattern: {pattern}")
            print(f"mode: {mode}")
            print(f"accuracy: {accuracy}")


if __name__ == "__main__":
    main()
