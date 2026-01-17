import json
import pandas as pd
import requests
import time

path = 'data/potential_matches.json'
sleep = 0.5


def get_freebase_id(city_name: str, country_name: str) -> str:
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
        print(f"No Freebase ID found for {city_name}")
        return None


freebase_ids = []
with open(path, "r", encoding="utf-8") as f:
    matches = json.load(f)[0]["Matches"]
matches_df = pd.DataFrame(matches)

for _, row in matches_df.iterrows():
    if row['City'] != 'Bray':
        freebase_ids.append(None)
        continue
    try:
        fb_id = get_freebase_id(row["City"], row["Country"])
        freebase_ids.append(fb_id)
        print(f"Received FreebaseID for {row['City']} ({fb_id})")
    except Exception as e:
        print(f"Error retrieving Freebase ID for {row['City']}, {row['Country']}: {e}")
        freebase_ids.append(None)
    time.sleep(sleep)  # polite rate limiting

df = matches_df.copy()
df["freebase_id"] = freebase_ids
print(df)
