from urllib.parse import urljoin

import scrapy


class UAHotelsSpider(scrapy.Spider):
    name = 'uahotels'
    custom_settings = {
        'ITEM_PIPELINES': {
            'db_lab_1.pipelines.NewsXmlPipeline': 300,
        }
    }
    start_urls = [
        'https://uahotels.info/'
    ]
    allowed_domains = [
        'uahotels.info'
    ]

    def parse(self, response):
        text = filter(lambda x: x, [x.strip() for x in response.xpath('//*[not(self::script)]/text()').getall()])
        images = [urljoin(response.url, url) for url in response.xpath('//img[@src]/@src').getall()]
        yield {
            'text': text,
            'images': images,
            'url': response.url
        }
        for link_url in response.xpath('//a[@href]/@href'):
            yield response.follow(link_url.extract(), callback=self.parse)
