import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class LiquidSpider(CrawlSpider):
    name = 'liquidspider'
    allowed_domains = ['liquipedia.net/starcraft2/']
    start_urls = ['https://liquipedia.net/starcraft2/Premier_Tournaments', "https://liquipedia.net/starcraft2/Major_Tournaments",
                   "https://liquipedia.net/starcraft2/Minor_Tournaments", "https://liquipedia.net/starcraft2/Monthly_Tournaments",
                   "https://liquipedia.net/starcraft2/Weekly_Tournaments", "https://liquipedia.net/starcraft2/Show_Matches",
                   "https://liquipedia.net/starcraft2/Female_Tournaments"]

    rules = (
        Rule(LinkExtractor(allow=r'/starcraft2', restrict_xpaths="//table/tbody/tr/td/a", ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['Tournament_link'] = response.xpath('//tr/').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item

