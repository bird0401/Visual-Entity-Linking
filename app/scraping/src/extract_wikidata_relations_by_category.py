from SPARQLWrapper import SPARQLWrapper, JSON
import json

# def query_ids_by_category(category):
#     category_to_query = {
#       "us_politician": 
#       """
#       SELECT ?id ?idLabel
#       WHERE {{
#         ?id wdt:P106 wd:Q82955;
#                 wdt:P27 wd:Q30.
#         ?id rdfs:label ?idLabel.
#         FILTER(LANG(?idLabel) = "en") .
#       }}
#       """,

#       "athlete": 
#       """
#       SELECT ?id ?idLabel
#       WHERE {
#         ?id wdt:P106 wd:Q2066131.
#         ?id rdfs:label ?idLabel.
#         FILTER(LANG(?idLabel) = "en") .
#       }
#       """,

#       "director": 
#       """
#       SELECT ?id ?idLabel
#       WHERE {
#         ?id wdt:P106 wd:Q2526255.
#         ?id rdfs:label ?idLabel.
#         FILTER(LANG(?idLabel) = "en") .
#       }
#       """,

#       "aircraft": 
#       """
#       SELECT ?id ?idLabel
#       WHERE {
#         ?id wdt:P31 wd:Q197.
#         ?id rdfs:label ?idLabel.
#         FILTER(LANG(?idLabel) = "en") .
#       }
#       """,

#       "car": 
#       """
#       SELECT ?id ?idLabel
#       WHERE {
#         ?id wdt:P31 wd:Q42889.
#         ?id rdfs:label ?idLabel.
#         FILTER(LANG(?idLabel) = "en") .
#       }
#       """,

#       "dog": 
#       """
#       SELECT  ?id ?idLabel
#       WHERE {
#         ?id wdt:P31 wd:Q39367.
#         ?id rdfs:label ?idLabel.
#         FILTER(LANG(?idLabel) = "en") .
#       }
#       """,

#       "bird": 
#       """
#       SELECT  ?id ?idLabel
#       WHERE {
#         ?id wdt:P279 wd:Q5113.
#         ?id rdfs:label ?idLabel.
#         FILTER(LANG(?idLabel) = "en") .
#       }
#       """,

#       "bread": 
#       """
#       SELECT  ?id ?idLabel
#       WHERE {
#         ?id wdt:P279 wd:Q7802.
#         ?id rdfs:label ?idLabel.
#         FILTER(LANG(?idLabel) = "en") .
#       }
#       """
#     }

#     # ids_str = " ".join([f"wd:{id}" for id in ids])
#     sparql = SPARQLWrapper("https://query.wikidata.org/sparql", returnFormat='json')
#     sparql.setReturnFormat(JSON)
#     sparql.setMethod('POST')
#     sparql.setQuery(category_to_query[category])
#     return sparql.queryAndConvert()["results"]["bindings"]


# def preprocess_res(relations):
#     id_to_relations = {}
#     for relation in relations:
#         id = relation["id"]["value"].split("/")[-1]
#         idLabel = relation["idLabel"]["value"]
#         if id not in id_to_relations:
#             id_to_relations[id] = {"relations": {}}
#         if "idLabel" not in id_to_relations[id]["relations"]:
#             id_to_relations[id]["relations"]["idLabel"] = [idLabel]
#     return id_to_relations


# def extract_wikidata_ids_by_category(category):
#     print("Category: ", category)
#     category_dir = f"../../../data/clean/{category}" # TODO: change to more general path
#     res = query_ids_by_category(category)
#     # print(f"len(res): {len(res)}")
#     preprocessed_res = preprocess_res(res)
#     with open(f'{category_dir}/ids_labels.json', 'w') as f:
#         json.dump(preprocessed_res, f, indent=2)

# query all relations of a list of entities
def extract_relations_from_wikidata(ids):
    ids_str = " ".join([f"wd:{id}" for id in ids])
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", returnFormat='json')
    sparql.setReturnFormat(JSON)
    sparql.setMethod('POST')
    sparql.setQuery(f"""
        SELECT ?entity ?entityLabel ?propLabel ?objLabel 
        WHERE {{
            VALUES ?entity {{ {ids_str} }}
            ?entity ?wdt_prop ?obj.
            ?prop wikibase:directClaim ?wdt_prop.
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}       
    """)
    return sparql.queryAndConvert()["results"]["bindings"]

def relations_to_dict(relations):
    id_to_relations = {}
    for relation in relations:
        id = relation["entity"]["value"].split("/")[-1]
        name = relation["entityLabel"]["value"]
        prop = relation["propLabel"]["value"]
        obj = relation["objLabel"]["value"]
        if id not in id_to_relations:
            id_to_relations[id] = {"relations": {}}
        if "name" not in id_to_relations[id]["relations"]:
            id_to_relations[id]["relations"]["name"] = [name]
        if prop not in id_to_relations[id]:
            id_to_relations[id]["relations"][prop] = []
        id_to_relations[id]["relations"][prop].append(obj)
    return id_to_relations

# extract ids using wikidata query that assigns categories
def extract_wikidata_relations_by_category(category):
        print(f"category: {category}")
        category_dir = f"../../../data/clean/{category}"
        with open(f'{category_dir}/ids_labels.json') as f:
            ids_labels = json.load(f)
        ids = list(ids_labels.keys())
        # ids = [entity_text_file.split(".")[0] for entity_text_file in os.listdir(f"{category_dir}/wikipedia")]
        # ids = ["Q1626771"]
        print(f"len(ids): {len(ids)}")
        relations = []
        for i in range(0, len(ids), 100):
            print(f"{i} / {len(ids)}")
            relations += extract_relations_from_wikidata(ids[i:i+100])
        
        # print("relations")
        # print(relations)
        # print()
        wikidata = relations_to_dict(relations)
        # print("wikidata")
        # print(wikidata)
        with open(f'{category_dir}/wikidata.json', 'w') as f:
            json.dump(wikidata, f, indent=2)


def main():
    categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    for category in categories:
      extract_wikidata_relations_by_category(category)

if __name__ == "__main__":
    main()
