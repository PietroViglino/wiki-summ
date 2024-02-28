import os
from geojson import Point, Feature, FeatureCollection, dump
from modules.wikidata import WikiDataQueryResults
from modules.utils import *
from modules.llm import *
import datetime as dt

CITY_NAME = 'Finale Ligure'

Q_IDs = {
    'Genova': 'Q1449',
    'Torino': 'Q495',
    'Finale Ligure': 'Q270737'
}

def job(city_name):
   try:
      q_id = Q_IDs[city_name]
   except:
       print('No Q_ID found with that name')
       logging.warn('No Q_ID found with that name')
       return 
   query = f"""
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
   logging.info(f'Starting job. {len(data)} total documents for {city_name}')
   features = []
   t_0 = dt.datetime.now()
   n = 0
   data = data[10:12] # split data to work in blocks. ex: :50, 50:100, 100:150, etc
   logging.info(f'Length of data selected for elaboration: {len(data)}')
   for index, doc in enumerate(data):
        name = doc.get('name')
        n = index
        logging.info(f'Started processing wiki article: {name}')
        url = doc.get('article')
        lon = float(doc.get('lon'))
        lat = float(doc.get('lat'))
        geometry = Point([lon, lat])
        logging.debug('Starting text and tags extraction from HTML')
        text, html_tags = extract_text_tags(url)
        logging.debug('Extraction completed. Starting summarization')
        summ_en, summ_ita = summs(text)
        features.append(Feature(geometry=geometry, properties={"name": name, "summary_en": summ_en, "summ_ita": summ_ita, "tags": html_tags}))
        logging.info(f'Finished processing wiki article: {name}')
        percentage = ((index + 1) / len(data)) * 100
        logging.info(f'{index + 1}/{len(data)}: job at {float(round(percentage,3))}%')
   feature_collection = FeatureCollection(features)
   city_name = city_name.replace('/', '_').replace(' ', '_')
   with open(f'output/poi_{city_name}.geojson', 'w', encoding='utf8') as f:
         dump(feature_collection, f, ensure_ascii=False)
   logging.info(f'Done generating geojson files for {city_name}')
   t_end = dt.datetime.now() - t_0
   logging.info(f'Processing {n + 1} documents took {str(t_end)}')
                      
if __name__ == '__main__':
   logger = logging.getLogger()    
   file_handler = logging.FileHandler(filename="logfile.log", mode="w")
   formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
   file_handler.setFormatter(formatter)
   logger.addHandler(file_handler)
   logger.setLevel(logging.DEBUG)
   try:
      job(CITY_NAME)
   except Exception as e:
       print(f'Error: {str(e)}')
