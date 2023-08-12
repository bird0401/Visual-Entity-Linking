import pandas as pd

def main():
    data_dir = "../../../data/clean"
    categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        csv_dir = f"{data_dir}/{category}/csv"
        df = pd.read_csv(f"{csv_dir}/origin.csv", dtype={"wikidata_id": str})
        print(category)
        ids = pd.DataFrame(df["wikidata_id"].unique())
        ids.columns = ["wikidata_id"]
        print((len(ids)))
        ids.to_csv(f"{csv_dir}/ids.csv")

if __name__ == "__main__":
    main()
