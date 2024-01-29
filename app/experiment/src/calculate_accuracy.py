from util import calculate_accuracy



def main():
    # categories = [sys.argv[1]]
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    
    patterns = [
        # {"name": False, "article": False, "relations": False, "confidence": False}, 
        # {"name": True, "article": False, "relations": False, "confidence": False}, 
        {"name": True, "article": True, "relations": False, "confidence": False}, 
        # {"name": True, "article": False, "relations": True, "confidence": False}, 
        # {"name": True, "article": True, "relations": True, "confidence": False}, 
        # {"name": True, "article": True, "relations": True, "confidence": True}, 
    ]

    for category in categories:
        qas_bem_path = f"../../../data/clean/{category}/qas_bem.json"
        for pattern in patterns:
            accuracy = calculate_accuracy(qas_bem_path, pattern)
            print(f"pattern: {pattern}")
            print(f"category: {category}")
            print(f"accuracy: {accuracy}")

if __name__ == "__main__":
    main()

    