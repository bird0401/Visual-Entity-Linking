from SPARQLWrapper import SPARQLWrapper, JSON
import pickle, json

def extract_relations_from_wikidata(id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", returnFormat='json')
    sparql.setReturnFormat(JSON)
    sparql.setMethod('POST')
    sparql.setQuery(f"""
        SELECT ?label ?place_of_birth ?sex_or_gender ?instance_of ?occupation ?award_received ?sport ?family_name ?participant_in ?given_name  ?place_of_death ?date_of_death ?manner_of_death ?cause_of_death ?place_of_burial ?educated_at ?significant_event ?described_by_source ?spouse ?languages_spoken ?country_for_sport ?father ?position_played_on_team ?work_period_start ?work_period_end ?mass ?sports_discipline_competed_in ?height ?sports_team ?country_of_citizenship ?date_of_birth
        WHERE
        {{
            OPTIONAL{{wd:{id} rdfs:label ?label. FILTER(LANG(?label)="en").}}
            OPTIONAL{{wd:{id} wdt:P19 ?o1. ?o1 rdfs:label ?place_of_birth. FILTER(LANG(?place_of_birth)="en").}}
            OPTIONAL{{wd:{id} wdt:P21 ?o2. ?o2 rdfs:label ?sex_or_gender. FILTER(LANG(?sex_or_gender)="en").}}      
            OPTIONAL{{wd:{id} wdt:P31 ?o3. ?o3 rdfs:label ?instance_of. FILTER(LANG(?instance_of)="en").}}
            OPTIONAL{{wd:{id} wdt:P106 ?o4. ?o4 rdfs:label ?occupation. FILTER(LANG(?occupation)="en").}}
            OPTIONAL{{wd:{id} wdt:P166 ?o5. ?o5 rdfs:label ?award_received. FILTER(LANG(?award_received)="en").}}
            OPTIONAL{{wd:{id} wdt:P641 ?o6. ?o6 rdfs:label ?sport. FILTER(LANG(?sport)="en").}}
            OPTIONAL{{wd:{id} wdt:P734 ?o7. ?o7 rdfs:label ?family_name. FILTER(LANG(?family_name)="en").}}
            OPTIONAL{{wd:{id} wdt:P1344 ?o8.  ?o8 rdfs:label ?participant_in. FILTER(LANG(?participant_in)="en").}}
            OPTIONAL{{wd:{id} wdt:P735 ?o9. ?o9 rdfs:label ?given_name. FILTER(LANG(?given_name)="en").}}
            OPTIONAL{{wd:{id} wdt:P20 ?o10. ?o10 rdfs:label ?place_of_death. FILTER(LANG(?place_of_death)="en").}}
            OPTIONAL{{wd:{id} wdt:P570 ?o11. ?o11 rdfs:label ?date_of_death. FILTER(LANG(?date_of_death)="en").}}
            OPTIONAL{{wd:{id} wdt:P1196 ?o12. ?o12 rdfs:label ?manner_of_death. FILTER(LANG(?manner_of_death)="en").}}
            OPTIONAL{{wd:{id} wdt:P509 ?o13. ?o13 rdfs:label ?cause_of_death. FILTER(LANG(?cause_of_death)="en").}}
            OPTIONAL{{wd:{id} wdt:P119 ?o14. ?o14 rdfs:label ?place_of_burial. FILTER(LANG(?place_of_burial)="en").}}
            OPTIONAL{{wd:{id} wdt:P69 ?o15. ?o15 rdfs:label ?educated_at. FILTER(LANG(?educated_at)="en").}}
            OPTIONAL{{wd:{id} wdt:P793 ?o16. ?o16 rdfs:label ?significant_event. FILTER(LANG(?significant_event)="en").}}
            OPTIONAL{{wd:{id} wdt:P1343 ?o17. ?o17 rdfs:label ?described_by_source. FILTER(LANG(?described_by_source)="en").}}
            OPTIONAL{{wd:{id} wdt:P26 ?o18. ?o18 rdfs:label ?spouse. FILTER(LANG(?spouse)="en").}}
            OPTIONAL{{wd:{id} wdt:P1412 ?o19. ?o19 rdfs:label ?languages_spoken. FILTER(LANG(?languages_spoken)="en").}}
            OPTIONAL{{wd:{id} wdt:P1532 ?o20. ?o20 rdfs:label ?country_for_sport. FILTER(LANG(?country_for_sport)="en").}}
            OPTIONAL{{wd:{id} wdt:P22 ?o21. ?o21 rdfs:label ?father. FILTER(LANG(?father)="en").}}
            OPTIONAL{{wd:{id} wdt:P413 ?o22. ?o22 rdfs:label ?position_played_on_team. FILTER(LANG(?position_played_on_team)="en").}}
            OPTIONAL{{wd:{id} wdt:P2031 ?o23. ?o23 rdfs:label ?work_period_start. FILTER(LANG(?work_period_start)="en").}}
            OPTIONAL{{wd:{id} wdt:P2032 ?o24. ?o24 rdfs:label ?work_period_end. FILTER(LANG(?work_period_end)="en").}}
            OPTIONAL{{wd:{id} wdt:P2067 ?o25. ?o25 rdfs:label ?mass. FILTER(LANG(?mass)="en").}}
            OPTIONAL{{wd:{id} wdt:P2416 ?o26. ?o26 rdfs:label ?sports_discipline_competed_in. FILTER(LANG(?sports_discipline_competed_in)="en").}}
            OPTIONAL{{wd:{id} wdt:P2048 ?o27. ?o27 rdfs:label ?height. FILTER(LANG(?height)="en").}}
            OPTIONAL{{wd:{id} wdt:P54 ?o28. ?o28 rdfs:label ?sports_team. FILTER(LANG(?sports_team)="en").}}
            OPTIONAL{{wd:{id} wdt:P27 ?o29. ?o29 rdfs:label ?country_of_citizenship. FILTER(LANG(?country_of_citizenship)="en").}}
            OPTIONAL{{wd:{id} wdt:P569 ?date_of_birth. }}
        }}           
    """)
    return sparql.queryAndConvert()["results"]["bindings"]

def main():
    categories = ["athlete"]
    for category in categories:
        with open(f'../../../data/clean/{category}/qa_mask.json') as f:
            qa_mask = json.load(f)
        ids = qa_mask.keys()
        # ids = ["Q4409204"]
        # print(ids)
        results = {}
        for id in ids:
            results[id] = extract_relations_from_wikidata(id)
        # print(results)
        for id in results:
            print(f"id: {id}\n")
            for i, result in enumerate(results[id]):
                print(f"result {i+1}:")
                for key in result:
                    print(f"{key}: {result[key]['value']}")
                print()
        with open(f'../../../data/clean/{category}/relations.pkl', 'wb') as f:
            pickle.dump(results, f)

if __name__ == "__main__":
    main()




