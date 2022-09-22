from json import loads

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse, parse_qs

from Scrapy.items import MinistryItem
from Scrapy.spiders.utils import clean


class Parser:

    def product_care(self, response):
        return clean(response.css('.AccordionGroup__text-block ::text').getall())

    def product_category(self, response):
        categories = clean(response.css('.Breadcrumb__linkText::text').getall())
        return categories[0:2]

    def product_description(self, response):
        return clean(response.css('.ProductMetaBody__description ::text').getall())

    def product_gender(self, response):
        gender_category = self.product_category(response)
        if 'all' in [gender.lower() for gender in gender_category]:
            return 'Unisex-adults'
        return gender_category[0]

    def product_colour(self, script):
        product_url = script['offers']['url']
        parsed_url = urlparse(product_url)
        colour = parse_qs(parsed_url.query)['color'][0]

        return colour

    def product_image_urls(self, response, script):
        urls = response.css('.ProductPage__carousel-image::attr(src)').getall()
        return {self.product_colour(script): urls}

    def product_name(self, response):
        return clean(response.css('.ProductMetaHeader__heading::text').get())

    def product_price(self, script):
        currency = script['offers']['priceCurrency']
        price = script['offers']['price']
        return price, currency
        
    def product_skus(self, response, script):
        size_options = clean(response.css('.BaseFormSelect__option::text').getall())
        common_sku = {}
        skus = {}
        common_sku['colour'] = self.product_colour(script)
        common_sku['currency'] = self.product_price(script)[1]
        common_sku['price'] = self.product_price(script)[0]
            
        for size in size_options:
            sku = common_sku.copy()
            sku['out_of_Stock'] = 'notifyme' in clean(size.lower())
            sku['size'] = size[0]
            skus[size[0]] = sku
            
        return skus

    def raw_product(self, response):
        script = loads(response.css('script:contains("sku")::text').get())
        return script

    def parse_items(self, response):
        item = MinistryItem()

        item['brand'] = self.raw_product(response)['brand']['name']
        item['gender'] = self.product_gender(response)
        item['name'] = self.product_name(response)
        item['retailer_sku'] = self.raw_product(response)['sku']
        item['url'] = self.raw_product(response)['offers']['url']

        item['care'] = self.product_care(response),
        item['category'] = self.product_category(response)
        item['description'] = self.product_description(response)

        item['image_urls'] = self.product_image_urls(response, self.raw_product(response))
        item['skus'] = self.product_skus(response, self.raw_product(response))

        yield item


class Crawler(CrawlSpider):

    name = 'ministryspider'
    start_urls = ['https://www.ministryofsupply.com/women/shop-all',
                  'https://www.ministryofsupply.com/men/shop-all']
    rules = (
        Rule(LinkExtractor(restrict_css='.CardProduct__link'), callback=Parser().parse_items),
    )

