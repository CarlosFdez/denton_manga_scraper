import redis
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
  
  results = []
  for link in links:
    (name, chapter) = link.text.rsplit(' ', 1)
    results.append( (name, int(chapter), link['href']) )
  return results

# TODO: Support more than just mangastream
class Scraper(object):
  def __init__(self):
    self.db = redis.StrictRedis(host='localhost', port=6379, db=0)
    self.manga = {}
    self.mangastream = []

  def add_manga(self, name, sources):
    self.manga[name] = sources
    if 'mangastream' in sources:
      self.mangastream.append(name)

  def scrape(self):
    results = []
    for (name, chapter, link) in mangastream_manga_list():
      if name in self.mangastream:
        if self.is_new(name, chapter):
          result = (name, chapter, link)
          results.append(result)
          self.record(result)
    return results

  def record(self, result):
    (name, chapter, link) = result
    chapter_key = "manga:%s:latest:chapter" % name
    link_key = "manga:%s:latest:link" % name
    self.db.set(chapter_key, chapter)
    self.db.set(link_key, link)

  def get_manga(self):
    results = []
    for name in self.manga.keys():
      link = self.db.get("manga:%s:latest:link" % name)
      if not link: continue
      chapter = int(self.db.get("manga:%s:latest:chapter" % name))
      results.append( (name, chapter, link) )
    return results

  def is_new(self, name, scraped_chapter):
    chapter = self.db.get("manga:%s:latest:chapter" % name)
    if chapter is None:
      return True
    return scraped_chapter > int(chapter)
