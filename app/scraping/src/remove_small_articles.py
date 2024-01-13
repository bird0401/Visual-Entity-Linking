import os

data_dir = "../../../data/clean"

def remove_small_articles(category):
    wikipedia_dir = f"{data_dir}/{category}/wikipedia"
    file_names = os.listdir(wikipedia_dir)
    for file_name in file_names:
        file_path = f"{wikipedia_dir}/{file_name}"
        with open(file_path) as f:
            lines = f.read()
        lines_split = lines.split()
        if len(lines_split) < 100:
            os.remove(file_path)
            print(f"Removed {file_path}")
            print(len(lines_split))
            print(f"lines: \n{lines}\n")

def main():
    # categories = ["aircraft"]
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        print(f"Start remove_small_articles({category}) ...")
        remove_small_articles(category)
        print(f"Finish")

if __name__ == "__main__":
    main()