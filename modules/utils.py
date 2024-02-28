import requests
from bs4 import BeautifulSoup
from translate import Translator
import re

translator= Translator(to_lang="it")

def extract_text_tags(url):
    try:
        response = requests.get(url=url,)
        soup = BeautifulSoup(response.content, 'html.parser')
        heading = soup.find(id="firstHeading")
        title = heading.text
        text = []
        parafs = soup.find_all("p", recursive=True)
        for p in parafs:
            p_content = p.text
            p_content = p_content.replace('\n', '')
            p_content = re.sub(r'\[[^\]]*\]', '', p_content)
            p_content = re.sub(r'\([^)]*\)', '', p_content)
            p_list = re.split(r'(?<![A-Z])\.\s', p_content)
            for sentence in p_list:
                if sentence != '':
                    if sentence[-1] != '.':
                        sentence += '.'
                    text.append(sentence)
        text = ' '.join(text)
        a_list = [_.contents for _ in soup.find_all('a', recursive=True)]
        i_list = [_.contents for _ in soup.find_all('i', recursive=True)]
        b_list = [_.contents for _ in soup.find_all('b', recursive=True)]
        tags = a_list + i_list + b_list
        tags.append([title])
        exclude = ['Informativa sulla privacy', 'Dichiarazione sui cookie', 'Informazioni su Wikipedia', 'Categorie', 'Vai alla navigazione',\
                    'Aggiungi collegamenti', 'Vai alla ricerca', 'Versione mobile', 'Avvertenze', 'condizioni d\'uso', 'Controllo di autorità', \
                    'GND', 'LCCN', 'WorldCat Identities', 'Sito ufficiale', 'Codice di condotta', 'Sviluppatori', 'Modifica collegamenti',\
                    'tutte le voci', 'Categoria', 'note', 'migliorare questa voce', 'UTC+1']
        tags = [str(_[0]) for _ in tags if _ != [] and _ is not None and _[0] is not None]
        tags = [re.sub(r"\([^()]*\)", "", _.replace('<b>', '').replace('</b>', '')) for _ in tags if 2 < len(_) < 30 and 'span' not in _ and '.' not in _ and ',' not in _\
                and '[' not in _ and 'Wikidata' not in _ and 'Wikimedia' not in _ and 'lccn' not in _.lower() and _ not in exclude\
                and 'VIAF' not in _ and '^' not in _ and not re.search(r'\d{5,}', _) and 'Voci con codice' not in _ and 'pag ' not in _\
                and 'Contestualizzare fonti' not in _ and not (_.isdigit() and len(_) > 4)] 
        return text, list(set(tags))
    except Exception as e:
      print('Something went wrong: ', e)

def split_text(text, n):
  chunks = text.split()
  punctuation = [".", "!", "?", "..."]
  for i in range(len(chunks) - 1, -1, -1):
    if chunks[i] in punctuation:
      chunks.insert(i + 1, chunks[i])
      chunks.pop(i)
  current_chunk = ""
  for chunk in chunks:
    if len(current_chunk) + len(chunk) + 1 <= n:
      current_chunk += " " + chunk
    else:
      if current_chunk:
        yield current_chunk.strip()
      current_chunk = chunk
  if current_chunk:
    yield current_chunk.strip()



