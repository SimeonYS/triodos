import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import TriodosItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class TriodosSpider(scrapy.Spider):
	name = 'triodos'
	start_urls = ['https://www.triodos.be/nl/nieuws']

	def parse(self, response):
		post_links = response.xpath('//a[@class="article-card__link"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//time/@datetime').get()
		if not date:
			date = response.xpath('//meta[@itemprop="dateModified"]/@content').get()
		title = response.xpath('(//h1)[1]/text()').get()
		content = response.xpath('(//div[@class="col-12 col-lg-8"])[1]//text()[not (ancestor::section[@class="pressofficer"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=TriodosItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
