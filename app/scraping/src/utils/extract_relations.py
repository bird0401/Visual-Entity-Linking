from SPARQLWrapper import SPARQLWrapper, JSON
import json, os

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
        entity = relation["entity"]["value"].split("/")[-1]
        prop = relation["propLabel"]["value"]
        obj = relation["objLabel"]["value"]
        if entity not in id_to_relations:
            id_to_relations[entity] = {"relations": {}}
        if prop not in id_to_relations[entity]:
            id_to_relations[entity]["relations"][prop] = []
        id_to_relations[entity]["relations"][prop].append(obj)
    return id_to_relations

def extract_relations_from_wikidata_by_categories(categories):
    for category in categories:
        print(category)
        category_dir = f"../../../data/clean/{category}"
        ids = [entity_text_file.split(".")[0] for entity_text_file in os.listdir(f"{category_dir}/wikipedia")]
        # ids = ["Q4409204"]
        print(f"len(ids): {len(ids)}")
        relations = extract_relations_from_wikidata(ids)
        wikidata = relations_to_dict(relations)
        with open(f'{category_dir}/wikidata.json', 'w') as f:
            json.dump(wikidata, f, indent=2)

def main():
    categories = ["athlete"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    extract_relations_from_wikidata_by_categories(categories)

if __name__ == "__main__":
    main()




# def extract_relations_from_wikidata(id):
#     sparql = SPARQLWrapper("https://query.wikidata.org/sparql", returnFormat='json')
#     sparql.setReturnFormat(JSON)
#     sparql.setMethod('POST')
#     sparql.setQuery(f"""
#         SELECT ?label ?place_of_birth ?sex_or_gender ?instance_of ?occupation ?award_received ?sport ?family_name ?participant_in ?given_name  ?place_of_death ?date_of_death ?manner_of_death ?cause_of_death ?place_of_burial ?educated_at ?significant_event ?described_by_source ?spouse ?languages_spoken ?country_for_sport ?father ?position_played_on_team ?work_period_start ?work_period_end ?mass ?sports_discipline_competed_in ?height ?sports_team ?country_of_citizenship ?date_of_birth
#         WHERE
#         {{
#             OPTIONAL{{wd:{id} rdfs:label ?label. FILTER(LANG(?label)="en").}}

#             OPTIONAL{{wd:{id} wdt:P19 ?o1. ?o1 rdfs:label ?place_of_birth. FILTER(LANG(?place_of_birth)="en").}}
#             OPTIONAL{{wd:{id} wdt:P21 ?o2. ?o2 rdfs:label ?sex_or_gender. FILTER(LANG(?sex_or_gender)="en").}}      
#             OPTIONAL{{wd:{id} wdt:P31 ?o3. ?o3 rdfs:label ?instance_of. FILTER(LANG(?instance_of)="en").}}
#             OPTIONAL{{wd:{id} wdt:P106 ?o4. ?o4 rdfs:label ?occupation. FILTER(LANG(?occupation)="en").}}
#             OPTIONAL{{wd:{id} wdt:P166 ?o5. ?o5 rdfs:label ?award_received. FILTER(LANG(?award_received)="en").}}
#             OPTIONAL{{wd:{id} wdt:P641 ?o6. ?o6 rdfs:label ?sport. FILTER(LANG(?sport)="en").}}
#             OPTIONAL{{wd:{id} wdt:P734 ?o7. ?o7 rdfs:label ?family_name. FILTER(LANG(?family_name)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1344 ?o8.  ?o8 rdfs:label ?participant_in. FILTER(LANG(?participant_in)="en").}}
#             OPTIONAL{{wd:{id} wdt:P735 ?o9. ?o9 rdfs:label ?given_name. FILTER(LANG(?given_name)="en").}}
#             OPTIONAL{{wd:{id} wdt:P20 ?o10. ?o10 rdfs:label ?place_of_death. FILTER(LANG(?place_of_death)="en").}}
#             OPTIONAL{{wd:{id} wdt:P570 ?o11. ?o11 rdfs:label ?date_of_death. FILTER(LANG(?date_of_death)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1196 ?o12. ?o12 rdfs:label ?manner_of_death. FILTER(LANG(?manner_of_death)="en").}}
#             OPTIONAL{{wd:{id} wdt:P509 ?o13. ?o13 rdfs:label ?cause_of_death. FILTER(LANG(?cause_of_death)="en").}}
#             OPTIONAL{{wd:{id} wdt:P119 ?o14. ?o14 rdfs:label ?place_of_burial. FILTER(LANG(?place_of_burial)="en").}}
#             OPTIONAL{{wd:{id} wdt:P69 ?o15. ?o15 rdfs:label ?educated_at. FILTER(LANG(?educated_at)="en").}}
#             OPTIONAL{{wd:{id} wdt:P793 ?o16. ?o16 rdfs:label ?significant_event. FILTER(LANG(?significant_event)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1343 ?o17. ?o17 rdfs:label ?described_by_source. FILTER(LANG(?described_by_source)="en").}}
#             OPTIONAL{{wd:{id} wdt:P26 ?o18. ?o18 rdfs:label ?spouse. FILTER(LANG(?spouse)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1412 ?o19. ?o19 rdfs:label ?languages_spoken. FILTER(LANG(?languages_spoken)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1532 ?o20. ?o20 rdfs:label ?country_for_sport. FILTER(LANG(?country_for_sport)="en").}}
#             OPTIONAL{{wd:{id} wdt:P22 ?o21. ?o21 rdfs:label ?father. FILTER(LANG(?father)="en").}}
#             OPTIONAL{{wd:{id} wdt:P413 ?o22. ?o22 rdfs:label ?position_played_on_team. FILTER(LANG(?position_played_on_team)="en").}}
#             OPTIONAL{{wd:{id} wdt:P2031 ?o23. ?o23 rdfs:label ?work_period_start. FILTER(LANG(?work_period_start)="en").}}
#             OPTIONAL{{wd:{id} wdt:P2032 ?o24. ?o24 rdfs:label ?work_period_end. FILTER(LANG(?work_period_end)="en").}}
#             OPTIONAL{{wd:{id} wdt:P2416 ?o26. ?o26 rdfs:label ?sports_discipline_competed_in. FILTER(LANG(?sports_discipline_competed_in)="en").}}
#             OPTIONAL{{wd:{id} wdt:P54 ?o28. ?o28 rdfs:label ?sports_team. FILTER(LANG(?sports_team)="en").}}
#             OPTIONAL{{wd:{id} wdt:P27 ?o29. ?o29 rdfs:label ?country_of_citizenship. FILTER(LANG(?country_of_citizenship)="en").}}

#             OPTIONAL{{wd:{id} wdt:P279 ?o. ?o rdfs:label ?subclass_of. FILTER(LANG(?subclass_of)="en").}}
#             OPTIONAL{{wd:{id} wdt:P366 ?o. ?o rdfs:label ?has_use. FILTER(LANG(?has_use)="en").}}
#             OPTIONAL{{wd:{id} wdt:P495 ?o. ?o rdfs:label ?country_of_origin. FILTER(LANG(?country_of_origin)="en").}}
#             OPTIONAL{{wd:{id} wdt:P137 ?o. ?o rdfs:label ?operator. FILTER(LANG(?operator)="en").}}
#             OPTIONAL{{wd:{id} wdt:P176 ?o. ?o rdfs:label ?manufacturer. FILTER(LANG(?manufacturer)="en").}}
#             OPTIONAL{{wd:{id} wdt:P516 ?o. ?o rdfs:label ?powered_by. FILTER(LANG(?powered_by)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1654 ?o. ?o rdfs:label ?wing_configuration. FILTER(LANG(?wing_configuration)="en").}}
#             OPTIONAL{{wd:{id} wdt:P373 ?o. ?o rdfs:label ?Commons_category. FILTER(LANG(?Commons_category)="en").}}
#             OPTIONAL{{wd:{id} wdt:P910 ?o. ?o rdfs:label ?topics_main_category. FILTER(LANG(?topics_main_category)="en").}}
#             OPTIONAL{{wd:{id} wdt:P607 ?o. ?o rdfs:label ?conflict. FILTER(LANG(?conflict)="en").}}
#             OPTIONAL{{wd:{id} wdt:P144 ?o. ?o rdfs:label ?based_on. FILTER(LANG(?based_on)="en").}}
#             OPTIONAL{{wd:{id} wdt:P178 ?o. ?o rdfs:label ?developer. FILTER(LANG(?developer)="en").}}
#             OPTIONAL{{wd:{id} wdt:P287 ?o. ?o rdfs:label ?designed_by. FILTER(LANG(?designed_by)="en").}}

#             OPTIONAL{{wd:{id} wdt:P105 ?o. ?o rdfs:label ?taxon_rank. FILTER(LANG(?taxon_rank)="en").}}
#             OPTIONAL{{wd:{id} wdt:P171 ?o. ?o rdfs:label ?parent_taxon. FILTER(LANG(?parent_taxon)="en").}}
#             OPTIONAL{{wd:{id} wdt:P3512 ?o. ?o rdfs:label ?means_of_locomotion. FILTER(LANG(?means_of_locomotion)="en").}}
#             OPTIONAL{{wd:{id} wdt:P462 ?o. ?o rdfs:label ?color. FILTER(LANG(?color)="en").}}
#             OPTIONAL{{wd:{id} wdt:P2572 ?o. ?o rdfs:label ?hashtag. FILTER(LANG(?hashtag)="en").}}
#             OPTIONAL{{wd:{id} wdt:P9714 ?o. ?o rdfs:label ?taxon_range. FILTER(LANG(?taxon_range)="en").}}
#             OPTIONAL{{wd:{id} wdt:P3113 ?o. ?o rdfs:label ?does_not_have_part. FILTER(LANG(?does_not_have_part)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1672 ?o. ?o rdfs:label ?this_taxon_is_source_of. FILTER(LANG(?this_taxon_is_source_of)="en").}}
#             OPTIONAL{{wd:{id} wdt:P2579 ?o. ?o rdfs:label ?studied_by. FILTER(LANG(?studied_by)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1552 ?o. ?o rdfs:label ?has_quality. FILTER(LANG(?has_quality)="en").}}
#             OPTIONAL{{wd:{id} wdt:P9566 ?o. ?o rdfs:label ?diel_cycle. FILTER(LANG(?diel_cycle)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1382 ?o. ?o rdfs:label ?partially_coincident_with. FILTER(LANG(?partially_coincident_with)="en").}}

#             OPTIONAL{{wd:{id} wdt:P361 ?o. ?o rdfs:label ?part_of. FILTER(LANG(?part_of)="en").}}
#             OPTIONAL{{wd:{id} wdt:P527 ?o. ?o rdfs:label ?has_part. FILTER(LANG(?has_part)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1889 ?o. ?o rdfs:label ?different_from. FILTER(LANG(?different_from)="en").}}
#             OPTIONAL{{wd:{id} wdt:P186 ?o. ?o rdfs:label ?made_from_material. FILTER(LANG(?made_from_material)="en").}}
#             OPTIONAL{{wd:{id} wdt:P8431 ?o. ?o rdfs:label ?course. FILTER(LANG(?course)="en").}}
#             OPTIONAL{{wd:{id} wdt:P2012 ?o. ?o rdfs:label ?cuisine. FILTER(LANG(?cuisine)="en").}}
#             OPTIONAL{{wd:{id} wdt:P138 ?o. ?o rdfs:label ?named_after. FILTER(LANG(?named_after)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1419 ?o. ?o rdfs:label ?shape. FILTER(LANG(?shape)="en").}}

#             OPTIONAL{{wd:{id} wdt:P155 ?o. ?o rdfs:label ?follows. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt:P156 ?o. ?o rdfs:label ?followed_by. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1716 ?o. ?o rdfs:label ?brand. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt:P1071 ?o. ?o rdfs:label ?location_of_creation. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt:P3039 ?o. ?o rdfs:label ?wheelbase. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt:P88 ?o. ?o rdfs:label ?commissioned_by. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt:P17 ?o. ?o rdfs:label ?country. FILTER(LANG(?country_of_citizenship)="en").}}
            
#             OPTIONAL{{wd:{id} wdt: ?o. ?o rdfs:label ?. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt: ?o. ?o rdfs:label ?. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt: ?o. ?o rdfs:label ?. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt: ?o. ?o rdfs:label ?. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt: ?o. ?o rdfs:label ?. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt: ?o. ?o rdfs:label ?. FILTER(LANG(?country_of_citizenship)="en").}}
#             OPTIONAL{{wd:{id} wdt: ?o. ?o rdfs:label ?. FILTER(LANG(?country_of_citizenship)="en").}}

#             OPTIONAL{{wd:{id} wdt:P606 ?first_flight.}}
#             OPTIONAL{{wd:{id} wdt:P2050 ?wingspan.}}
#             OPTIONAL{{wd:{id} wdt:P1092 ?total_produced.}}
#             OPTIONAL{{wd:{id} wdt:P729 ?service_entry.}}
#             OPTIONAL{{wd:{id} wdt:P2043 ?length.}}
#             OPTIONAL{{wd:{id} wdt:P730 ?service_retirement.}}

#             OPTIONAL{{wd:{id} wdt:P569 ?date_of_birth. }}
#             OPTIONAL{{wd:{id} wdt:P2048 ?height.}}
#             OPTIONAL{{wd:{id} wdt:P2067 ?mass.}}

#             OPTIONAL{{wd:{id} wdt:P225 ?taxon name.}}
#             OPTIONAL{{wd:{id} wdt:P1843 ?taxon common name.}}
#             OPTIONAL{{wd:{id} wdt:Q10856 ?Columbidae.}}
#             OPTIONAL{{wd:{id} wdt:P7725 ?litter size.}}
#             OPTIONAL{{wd:{id} wdt:P7770 ?egg incubation period.}}
#             OPTIONAL{{wd:{id} wdt:P7862 ?period of lactation.}}
#             OPTIONAL{{wd:{id} wdt:P1813 ?short name.}}
#             OPTIONAL{{wd:{id} wdt:P580 ?start time.}}}}            

#             OPTIONAL{{wd:{id} wdt:P1705 ?native_label.}}

#             OPTIONAL{{wd:{id} wdt:P2049 ?width.}}
#             OPTIONAL{{wd:{id} wdt:P2669 ?discontinued_date.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#             OPTIONAL{{wd:{id} wdt: ?.}}
#         }}           
#     """)
#     return sparql.queryAndConvert()["results"]["bindings"]