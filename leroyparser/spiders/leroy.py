import scrapy
from scrapy.http import HtmlResponse
from leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader

class LeroySpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']")
        if next_page:
            yield response.follow(next_page[0], callback=self.parse)
        links = response.xpath("//a[@class='bex6mjh_plp b1f5t594_plp iypgduq_plp nf842wf_plp']/@href")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyparserItem(), response=response)

        loader.add_xpath('name', "//h1[@slot='title']/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('images', "//picture[@slot='pictures']/source [@media=' only screen and (min-width: 1024px)']/@data-origin")
        loader.add_value('url', response.url)
        yield loader.load_item()
