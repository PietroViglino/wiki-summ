import logging
import os
from geojson import Point, Feature, FeatureCollection, dump
from wikidata import WikiDataQueryResults
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
   logging.info(f'Starting job. {len(data)} articles to process')
   for index, doc in enumerate(data):
            name = doc.get('name')
            if name + '.geojson' not in os.listdir('output/'):
               logging.debug(f'Started processing wiki article: {name}')
               features = []
               url = doc.get('article')
               lon = float(doc.get('lon'))
               lat = float(doc.get('lat'))
               geometry = Point([lon, lat])
               text = extract_text(url)
               summ_en, summ_ita, tags = summs_tags(text)
               features.append(Feature(geometry=geometry, properties={"name": name, "summary_en": summ_en, "summ_ita": summ_ita, "tags": tags}))
               feature_collection = FeatureCollection(features)
               name = name.replace('/', '_').replace(' ', '_')
               with open(f'output/{name}.geojson', 'w') as f:
                  dump(feature_collection, f)
               logging.debug(f'Finished summarizing and extracting tags for: {name}')
            else:
                logging.debug(f'Skipping {name}.geojson as it was already in output/ folder')
            percentage = ((index + 1) / len(data)) * 100
            logging.debug(f'Job at {percentage}%')
   logging.info(f'Done generating geojson files for {q_id}')
                      
if __name__ == '__main__':
   logger = logging.getLogger()    
   file_handler = logging.FileHandler(filename="logfile.log", mode="w")
   formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
   file_handler.setFormatter(formatter)
   logger.addHandler(file_handler)
   logger.setLevel(logging.DEBUG)
   try:
      job(Q_ID)
   except Exception as e:
       print(f'Error: {str(e)}')