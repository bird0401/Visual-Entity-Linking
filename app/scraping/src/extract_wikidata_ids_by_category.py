from SPARQLWrapper import SPARQLWrapper, JSON
import json

# import sys
# sys.path.append('./utils')
# from extract_relations import *

def query_ids_by_category(category):
    category_to_query = {
      "us_politician": 
      """
      SELECT ?id ?idLabel
      WHERE {{
        ?id wdt:P106 wd:Q82955;
                wdt:P27 wd:Q30.
        ?id rdfs:label ?idLabel.
        FILTER(LANG(?idLabel) = "en") .
      }}
      """,

      "athlete": 
      """
      SELECT ?id ?idLabel
      WHERE {
        ?id wdt:P106 wd:Q2066131.
        ?id rdfs:label ?idLabel.
        FILTER(LANG(?idLabel) = "en") .
      }
      """,

      "director": 
      """
      SELECT ?id ?idLabel
      WHERE {
        ?id wdt:P106 wd:Q2526255.
        ?id rdfs:label ?idLabel.
        FILTER(LANG(?idLabel) = "en") .
      }
      """,

      "aircraft": 
      """
      SELECT ?id ?idLabel
      WHERE {
        ?id wdt:P31 wd:Q197.
        ?id rdfs:label ?idLabel.
        FILTER(LANG(?idLabel) = "en") .
      }
      """,

      "car": 
      """
      SELECT ?id ?idLabel
      WHERE {
        ?id wdt:P31 wd:Q42889.
        ?id rdfs:label ?idLabel.
        FILTER(LANG(?idLabel) = "en") .
      }
      """,

      "dog": 
      """
      SELECT  ?id ?idLabel
      WHERE {
        ?id wdt:P31 wd:Q39367.
        ?id rdfs:label ?idLabel.
        FILTER(LANG(?idLabel) = "en") .
      }
      """,

      "bird": 
      """
      SELECT  ?id ?idLabel
      WHERE {
        ?id wdt:P279 wd:Q5113.
        ?id rdfs:label ?idLabel.
        FILTER(LANG(?idLabel) = "en") .
      }
      """,

      "bread": 
      """
      SELECT  ?id ?idLabel
      WHERE {
        ?id wdt:P279 wd:Q7802.
        ?id rdfs:label ?idLabel.
        FILTER(LANG(?idLabel) = "en") .
      }
      """
    }

    # ids_str = " ".join([f"wd:{id}" for id in ids])
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", returnFormat='json')
    sparql.setReturnFormat(JSON)
    sparql.setMethod('POST')
    sparql.setQuery(category_to_query[category])
    return sparql.queryAndConvert()["results"]["bindings"]


def preprocess_res(relations):
    id_to_relations = {}
    for relation in relations:
        id = relation["id"]["value"].split("/")[-1]
        idLabel = relation["idLabel"]["value"]
        if id not in id_to_relations:
            id_to_relations[id] = {"relations": {}}
        if "idLabel" not in id_to_relations[id]["relations"]:
            id_to_relations[id]["relations"]["idLabel"] = [idLabel]
    return id_to_relations


def extract_wikidata_ids_by_category(category):
    print("Category: ", category)
    category_dir = f"../../../data/clean/{category}" # TODO: change to more general path
    res = query_ids_by_category(category)
    preprocessed_res = preprocess_res(res)
    print(f"len(ids): {len(preprocessed_res)}")
    with open(f'{category_dir}/ids_labels.json', 'w') as f:
        json.dump(preprocessed_res, f, indent=2)


# Collect ids and labels of assignated categories from wikidata
def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
        extract_wikidata_ids_by_category(category)


if __name__ == "__main__":
    main()