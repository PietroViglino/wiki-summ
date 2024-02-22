from wikidata import *
from utils import *
from llm import *

Q_ID = 'Q1449'

def job(q_id):
   query= f"""
SELECT DISTINCT ?item ?name ?coord ?lat ?lon ?article

WHERE
{{
 hint:Query hint:optimizer "None" .
 ?item wdt:P131* wd:{q_id} .
 ?article schema:about ?item ; schema:isPartOf <https://it.wikipedia.org/>.
 ?item wdt:P625 ?coord .
 ?item p:P625 ?coordinate .
 ?coordinate psv:P625 ?coordinate_node .
 ?coordinate_node wikibase:geoLatitude ?lat .
 ?coordinate_node wikibase:geoLongitude ?lon .
 SERVICE wikibase:label {{
 bd:serviceParam wikibase:language "it" .
 ?item rdfs:label ?name
 }}
}}
ORDER BY ASC (?name)
"""
   data_extracter = WikiDataQueryResults(query)
   data = data_extracter._load()
   features = []
   for doc in data[:5]:
            name = doc.get('name')
            url = doc.get('article')
            lon = float(doc.get('lon'))
            lat = float(doc.get('lat'))
            geometry = Point([lon, lat])
            text = extract_text(url)
            summ_en, summ_ita = summarize(text, translate=False)
            # print(name, '\n')
            # print(summ_en, '\n')
            # print(summ_ita, '\n')
            features.append(Feature(geometry=geometry, properties={"name": name, "summary_en": summ_en, "summ_ita": summ_ita}))
   feature_collection = FeatureCollection(features)
   with open(f'{q_id}.geojson', 'w') as f:
      dump(feature_collection, f)
                      
if __name__ == '__main__':
   job(Q_ID)