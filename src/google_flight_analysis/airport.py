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
                
                VALUES ?cityType {{ wd:Q515 wd:Q15284 wd:Q3957 wd:Q532 wd:Q46831 wd:Q23442 wd:Q486972 }}
                
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
        