import json
import requests

class Airport():
    def __init__(self):
        self.dictionary = {
            'BER': 'Berlin',
            'BIO': 'Bilbao',
            'BRE': 'Bremen',
            'GRX': 'Granada',
            'LBC': 'Lubeck',
            'HAM': 'Hamburg',
            'MAD': 'Madrid',
            'AGP': 'Malaga',
            'FMM': 'Memmingen',
            'MUC': 'Munich',
            'SVQ': 'Sevilla',
            'VIT': 'Vitoria',
            
            # 'Berlin': 'BER',
            # 'Bilbao': 'BIO',
            # 'Bremen': 'BRE',
            # 'Granada': 'GRX',
            # 'Lubeck': 'LBC',
            # 'Hamburg': 'HAM',
            # 'Madrid': 'MAD',
            # 'Malaga': 'AGP',
            # 'Memmingen': 'FMM',
            # 'Munich': 'MUC',
            # 'Sevilla': 'SVQ',
            # 'Vitoria': 'VIT',
        }

    def to_iata(self, airport_name):
        return self.dictionary[airport_name]
    

    @staticmethod
    def city_from_iata(iata_code: str) -> str:
        if iata_code is None:
            return None

        with open('data/airport_codes.json', "r", encoding="utf-8") as f:
            city_iatas = json.load(f)
        city_name = next((city for city in city_iatas.keys() if iata_code in city_iatas[city]), None)
        if city_name:
            return city_name


        SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

        QUERY_TEMPLATE = """
        SELECT ?cityLabel WHERE {{
            ?airport wdt:P238 "{iata}" ;
                    wdt:P931 ?city .

            SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "en".
            }}
        }}
        LIMIT 1
        """

        headers = {
            "Accept": "application/sparql+json",
            "User-Agent": "FlightTracker/1.0 (contact: seguidor.pilideivid@gmail.com)"
        }


        query = QUERY_TEMPLATE.format(
            iata=iata_code.replace('"', '\\"'),
        )


        response = requests.get(
            SPARQL_ENDPOINT,
            params={
                "query": query,
                "format": "json"
            },
            headers=headers,
            timeout=90
        )

        data = response.json()
        bindings = data["results"]["bindings"]

        if bindings:
            city_name = bindings[0]["cityLabel"]["value"]

            if city_name in city_iatas:
                city_iatas[city_name].append(iata_code)
            else:
                city_iatas[city_name] = [iata_code]

            with open("data/airport_codes.json", "w+", encoding="utf-8") as f:
                json.dump(city_iatas, f, indent=4, ensure_ascii=False)

            return city_name
        else:
            print(f"No city found for IATA code {iata_code}")
            return None
    

    def to_freebase_id(self, city_name: str, country_name: str) -> str:
        if city_name == 'Majorca':
            city_name = 'Mallorca'

        SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

        QUERY_TEMPLATE = """
            SELECT ?city ?country ?freebaseID WHERE {{
                ?city rdfs:label "{city}"@en ;
                        wdt:P31/wdt:P279* ?cityType ;
                        wdt:P17 ?country ;
                        wdt:P646 ?freebaseID .
                
                VALUES ?cityType {{ 
                    wd:Q515
                    wd:Q15284 
                    wd:Q3957 
                    wd:Q532 
                    wd:Q46831 
                    wd:Q23442 
                    wd:Q486972 
                    wd:Q1549591 
                    wd:Q108178728
                    wd:Q200250
                }}
                
                ?country rdfs:label "{country}"@en .
            }}

            LIMIT 1
        """

        headers = {
            "Accept": "application/sparql+json",
            "User-Agent": "FlightTracker/1.0 (contact: seguidor.pilideivid@gmail.com)"
        }

        query = QUERY_TEMPLATE.format(
            city=city_name.replace('"', '\\"'),
            country=country_name.replace('"', '\\"')
        )


        response = requests.get(
            SPARQL_ENDPOINT,
            params={
                "query": query,
                "format": "json"
            },
            headers=headers,
            timeout=90
        )

        data = response.json()
        bindings = data["results"]["bindings"]

        if bindings:
            freebase_id = bindings[0]["freebaseID"]["value"]
            return freebase_id
        else:
            return None
        