import requests
from bs4 import BeautifulSoup

# Todo: There should probably be some sort of "driver" system
def mangastream_manga_list():
  r = requests.get('http://mangastream.com')
  if r.status_code != 200:
    print 'ERROR: Failed to load mangastream'
    return []
  soup = BeautifulSoup(r.text)
  links = soup.find('ul', 'freshmanga').find_all("a")
  return map(lambda x: (x.text.strip(), x['href']), links)

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
    results = []
    for (manga, link) in mangastream_manga_list():
      (name, chapter) = manga.rsplit(' ', 1)
      chapter = int(chapter)
      if name in self.mangastream:
        results.append( (name, chapter, link) )
    return results
       
