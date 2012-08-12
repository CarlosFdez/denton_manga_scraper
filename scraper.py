import os, re
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
      host, port, password = 'localhost', 6379, None
    else:
      url = os.environ['REDISTOGO_URL']
      password, host, port = re.match(r'redis://redistogo:([^@]+)@([^:]+):(\d+)', url).groups()
      port = int(port)
    self.db = redis.StrictRedis(host = host, port = port, password = password)
    self.manga = {}
    self.mangastream = []
    self.mangahere = []

  def add_manga(self, name, sources):
    """Registers a manga to be scraped. 
    
    Arguments:
    name -- The name of the manga to be added. ex: "Soul Eater"
    sources -- A list of sources for the manga. Currently, mangastream and
               mangahere are supported: 
               
    """
    self.manga[name] = sources
    if 'mangastream' in sources:
      self.mangastream.append(name)
    if 'mangahere' in sources:
      self.mangahere.append(name)

  def scrape(self):
    """Scrape for new manga, and returns (name, chapter, link) tuples"""
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
  
  def registered_manga(self):
    """Returns a list of registered manga in alphabetical order"""
    return sorted(self.manga.keys())
  
  def get_manga(self, name):
    """"
    Returns a (name, chapter#, link) tuple for the given chapter,
    or None if its not registered
    """
    if name not in self.manga.keys(): return None
    chapter = int(self.db.get("manga:%s:latest:chapter" % name))
    link = self.db.get("manga:%s:latest:link" % name)
    return (name, chapter, link)
  
  def get_all_manga(self):
    """Returns a list of manga info (name, chapter#, link) tuples"""
    results = []
    for name in self.manga.keys():
      manga = self.get_manga(name)
      if not manga[2]: continue
      results.append(manga)
    return results

  def is_new(self, name, scraped_chapter):
    chapter = self.db.get("manga:%s:latest:chapter" % name)
    if chapter is None:
      return True
    return scraped_chapter > int(chapter)
