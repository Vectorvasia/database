BOT_NAME = 'db_lab_1'

SPIDER_MODULES = ['db_lab_1.spiders']
NEWSPIDER_MODULE = 'db_lab_1.spiders'
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 16
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.closespider.CloseSpider': 100,
    'scrapy.extensions.logstats.LogStats': None,
    'scrapy.extensions.memusage.MemoryUsage': None,
    'scrapy.extensions.corestats.CoreStats': None
}

CLOSESPIDER_PAGECOUNT = 20
ROBOTSTXT_OBEY = False
