import scrapy


class MinistryItem(scrapy.Item):

    brand = scrapy.Field()
    gender = scrapy.Field()
    name = scrapy.Field()
    retailer_sku = scrapy.Field()
    url = scrapy.Field()
    color = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()

    care = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()

    image_urls = scrapy.Field()
    skus = scrapy.Field()
