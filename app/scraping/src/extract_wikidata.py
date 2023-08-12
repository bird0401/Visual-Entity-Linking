from SPARQLWrapper import SPARQLWrapper, JSON

def main():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", returnFormat='json')
    sparql.setReturnFormat(JSON)
    sparql.setQuery("""
        SELECT  ?id_us_politician ?name ?image ?date_of_birth ?date_of_death ?place_of_birth ?place_of_death ?sex_or_gender ?member_of_political_party
        WHERE {
        ?id_us_politician wdt:P106 wd:Q82955 ;
                    wdt:P27 wd:Q30 ;
                    wdt:P18 ?image ;
                    wdt:P19 ?object1 ;
                    wdt:P20 ?object2 ;
                    wdt:P21 ?object3 ;
                    wdt:P102 ?object5 ;
                    wdt:P569 ?date_of_birth ;
                    wdt:P570 ?date_of_death .
            ?id_us_politician rdfs:label ?name .
            ?object1 rdfs:label ?place_of_birth .
            ?object2 rdfs:label ?place_of_death .
            ?object3 rdfs:label ?sex_or_gender .
            ?object5 rdfs:label ?member_of_political_party .
            FILTER(LANG(?name) = "en") .
            FILTER(LANG(?place_of_birth) = "en") .
            FILTER(LANG(?place_of_death) = "en") .
            FILTER(LANG(?sex_or_gender) = "en") .
            FILTER(LANG(?member_of_political_party) = "en") .
        }
        """
    )
    try:
        results = sparql.queryAndConvert()
        # results = sparql_wikidata.query().convert()
        print(type(results))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()