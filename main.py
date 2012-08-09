import socket
import os
import pyrc
import pyrc.utils.hooks as hooks
from scraper import Scraper

CHANNELS = os.environ.get('BOT_CHANNELS', '##').split(',')

class DentonBot(pyrc.Bot):
  def __init__(self, *args, **kwargs):
    super(DentonBot, self).__init__(*args, **kwargs)
    self.scraper = Scraper()

    # todo: add mangastream to these as well
    self.scraper.add_manga('One Piece', ['mangahere'])
    self.scraper.add_manga('Bleach', ['mangahere'])
    self.scraper.add_manga('Naruto', ['mangahere'])
    self.scraper.add_manga('Fairy Tail', ['mangahere'])

    self.scraper.add_manga('Toriko', ['mangahere'])
    self.scraper.add_manga('Cage of Eden', ['mangahere'])
    self.scraper.add_manga('Gamaran', ['mangahere'])
    self.scraper.add_manga('Magi', ['mangahere'])
    self.scraper.add_manga('Shaman King Flowers', ['mangahere'])
    self.scraper.add_manga('Soul Eater', ['mangahere'])
    self.scraper.add_manga('The Breaker: New Waves', ['mangahere'])
    self.scraper.add_manga('The World God Only Knows', ['mangahere'])
    self.scraper.add_manga('Until Death Do Us Part', ['mangahere'])
    self.scraper.add_manga('Witch Hunter', ['mangahere'])
    self.scraper.add_manga('Yotsubato!', ['mangahere'])

  @hooks.command()
  def help(self, channel):
    self.message(channel, "You're gonna burn, all right.")

  @hooks.command(r"list|registered")
  def registered(self, channel):
    manga = self.scraper.registered_manga()
    manga_str = ', '.join(manga)
    self.message(channel, 'Registered manga include %s' % manga_str)

  @hooks.command("fetch manga")
  def fetch_manga(self, channel):
    results = self.scraper.get_manga()
    for (name, chapter, link) in results:
      self.message(channel, '%s %i: %s' % (name, chapter, link))

  @hooks.interval(2 * 60 * 1000)
  def scrape(self):
    results = self.scraper.scrape()
    for (name, chapter, link) in results:
      msg = 'New %s (%i): %s' % (name, chapter, link)
      for channel in CHANNELS:
        self.message(channel, msg)

  def close(self):
    super(DentonBot, self).close()
    if self.heroku_socket:
      self.heroku_socket.shutdown()
      self.heroku_socket.close()

if __name__ == '__main__':
  bot = DentonBot('irc.synirc.net',
    nick='JCDenton',
    names=['JC', 'JCDenton', 'Denton', 'JCD'],
    realname='JC Denton Bot',
    password="iamskynet",
    channels=CHANNELS)
  bot.connect()
