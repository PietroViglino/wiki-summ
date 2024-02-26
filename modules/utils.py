import requests
from bs4 import BeautifulSoup
from translate import Translator
import re

translator= Translator(to_lang="it")

def extract_text(url):
    try:
        response = requests.get(url=url,)
        soup = BeautifulSoup(response.content, 'html.parser')
        # heading = soup.find(id="firstHeading")
        # title = heading.text
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
        return text
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



