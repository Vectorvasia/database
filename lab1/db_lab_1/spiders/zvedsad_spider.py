from urllib.parse import urljoin

import scrapy


class ZvetsadSpider(scrapy.Spider):
    name = "zvetsad"
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 0,
        'CLOSESPIDER_ITEMCOUNT': 20
    }
    start_urls = [
        'https://www.zvetsad.com.ua/catalog/klematisyi'
    ]
    allowed_domains = [
        'zvetsad.com.ua'
    ]

    def parse(self, response):
        for product in response.xpath('//div[@class="item_div"]'):
            yield {
                'link': product.xpath('.//div[@class="item_nazvanie"]//a/@href').get(),
                'price': product.xpath('.//div[@class="price fl"]//text()').get(),
                'img': product.xpath('.//div[@class="r"]//img/@src').get(),
                'name': product.xpath('.//div[@class="item_nazvanie"]//a/text()').get().strip()
            }
