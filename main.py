import pyrc
import pyrc.utils.hooks as hooks
from scraper import Scraper

class DentonBot(pyrc.Bot):
  def __init__(self, *args, **kwargs):
    super(DentonBot, self).__init__(*args, **kwargs)
    self.scraper = Scraper()
    self.scraper.add_manga('Naruto', ['mangastream'])
    
  @hooks.command
  def bling(self, channel):
    self.message(channel, "yo")
    
  @hooks.interval(15000)
  def scrape(self):
    results = self.scraper.scrape()
    for (name, chapter) in results:
      self.message('#testchannel', 'New %s' % name)
  
if __name__ == '__main__':
  bot = DentonBot('irc.synirc.net', 
    nick='JCDenton',
    #names=['JC', 'JCDenton', 'Denton', 'JCD'],
    realname='JC Denton Bot',
    channels=['#testchannel'])
  bot.connect()
