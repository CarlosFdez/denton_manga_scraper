import os
import pyrc
import pyrc.utils.hooks as hooks
from scraper import Scraper

CHANNELS = os.environ.get('BOT_CHANNELS', 'testchannel').split(',')

class DentonBot(pyrc.Bot):
  def __init__(self, *args, **kwargs):
    super(DentonBot, self).__init__(*args, **kwargs)
    self.scraper = Scraper()
    self.scraper.add_manga('One Piece', ['mangastream'])
    self.scraper.add_manga('Bleach', ['mangastream'])
    self.scraper.add_manga('Naruto', ['mangastream'])
    self.scraper.add_manga('Toriko', ['mangahere'])
    self.scraper.add_manga('Gamaran', ['mangahere'])
    self.scraper.add_manga('Soul Eater', ['mangahere'])

  @hooks.command
  def help(self, channel):
    self.message(channel, "You're gonna burn, all right.")

  @hooks.interval(15000)
  def scrape(self):
    results = self.scraper.scrape()
    for (name, chapter, link) in results:
      msg = 'New %s (%i): %s' % (name, chapter, link)
      for channel in CHANNELS:
        self.message(channel, msg)

  @hooks.command
  def fetch_manga(self, channel):
    results = self.scraper.get_manga()
    for (name, chapter, link) in results:
      self.message(channel, "%s %i: %s" % (name, chapter, link))

if __name__ == '__main__':
  bot = DentonBot('irc.synirc.net',
    nick='JCDenton',
    names=['JC', 'JCDenton', 'Denton', 'JCD'],
    realname='JC Denton Bot',
    channels=CHANNELS)
  bot.connect()
