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
  return map(lambda x: (x.text.strip(), x['href']), links)

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

    # Add new manga to an array.
    for (manga, link) in mangastream_manga_list():
      (name, chapter) = manga.rsplit(' ', 1)
      chapter = int(chapter)
      if name in self.mangastream:
        if self.is_new(name, chapter):
          result = (name, chapter, link)
          results.append(result)

    # Results are recorded afterward.
    # This is so we consistently get batches of new chaps.
    for result in results:
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
