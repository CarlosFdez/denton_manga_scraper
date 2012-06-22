import os
import redis
import requests
from bs4 import BeautifulSoup

try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

# TODO: There should probably be some sort of "driver" system
# TODO: Don't get a request from mangastream / mangahere if no manga goes there

def mangastream_scrape(manga_list):
  r = requests.get('http://mangastream.com')
  if r.status_code != 200:
    print 'ERROR: Failed to load mangastream'
    return []
  soup = BeautifulSoup(r.text)
  links = soup.find('ul', 'freshmanga').find_all("a")

  results = []
  for link in links:
    (name, chapter) = link.text.rsplit(' ', 1)
    if name not in manga_list: continue
    result = (name, int(chapter), link['href'])
    results.append(result)
  return results

def mangahere_scrape(manga_list):
  r = requests.get('http://mangahere.com')
  if r.status_code != 200:
    print 'ERROR: Failed to load mangahere'
    return []
  soup = BeautifulSoup(r.text)
  links = soup.find('div', 'manga_updates').select("dd a")

  results = []
  for link in links:
    (name, chapter) = link.text.rsplit(' ', 1)
    if name not in manga_list: continue
    result = (name, int(chapter), link['href'])
    results.append(result)
  return results

# TODO: Support more than just mangastream
class Scraper(object):
  def __init__(self):
    if 'REDISTOGO_URL' not in os.environ:
      host, port = 'localhost', 6379
    else:
      parsed_url = urlparse(os.environ['REDISTOGO_URL'])
      host, port = parsed_url.host, parsed_url.port
    self.db = redis.StrictRedis(host = host, port = port)
    self.manga = {}
    self.mangastream = []
    self.mangahere = []

  def add_manga(self, name, sources):
    self.manga[name] = sources
    if 'mangastream' in sources:
      self.mangastream.append(name)
    if 'mangahere' in sources:
      self.mangahere.append(name)

  def scrape(self):
    results = []

    # Grab manga
    manga_info = mangastream_scrape(self.mangastream)
    manga_info += mangahere_scrape(self.mangahere)
    for (name, chapter, link) in manga_info:
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
