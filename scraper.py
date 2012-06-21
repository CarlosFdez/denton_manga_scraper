import requests
from bs4 import BeautifulSoup

# TODO: Support more than just mangastream
class Scraper(object):
  def __init__(self, *args, **kwargs):
    self.manga = {}
    self.mangastream = []
    
  def add_manga(self, name, sources):
    self.manga[name] = sources
    if 'mangastream' in sources:
      self.mangastream.append(name)
    
  def scrape(self):
    r = requests.get('http://mangastream.com')
    if r.status_code != 200:
      print 'ERROR: Failed to load mangastream'
      return []
    soup = BeautifulSoup(r.text)
    links = soup.find('ul', 'freshmanga').find_all("a")
    mangas = map(lambda x: x.text.strip(), links)
    
    results = []
    for manga in mangas:
      (name, chapter) = manga.rsplit(' ', 1)
      chapter = int(chapter)
      if name in self.mangastream:
        results.append( (name, chapter) )
    return results
       
