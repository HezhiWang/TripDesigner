# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class AttractioncrawlerSpider(CrawlSpider):
    name = 'attractioncrawler'
    allowed_domains = ['tripadvisor.com' , 'www.tripadvisor.com/Attractions']

    def __init__(self, *args, **kwargs):
        super(AttractioncrawlerSpider, self).__init__(*args, **kwargs)
        self.url = kwargs.get('url')
        self.start_urls = [self.url]
        self.number_of_attractions = 0

    def parse_start_url(self, response):
        links = response.css('div.listing_commerce a::attr(href)').extract()
            
        for link in links:
            yield response.follow(link, callback=self.parse_attraction)
 
        next_page = response.css('a.nav.next.rndBtn.ui_button.primary.taLnk::attr(href)').extract_first()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_attraction(self, response):
        attraction = {}
        self.number_of_attractions += 1
        print(self.number_of_attractions) 
        title = response.css('#HEADING::text').extract_first()
        
        rating= response.css('span.header_rating div span::attr(content)').extract_first()
        reviews = response.css("span.header_rating div a span::text").extract_first()
        reviews = int(reviews.replace(",",""))

        description = response.xpath("//*[@id='taplc_location_detail_overview_attraction_0']/div/div[2]/div[2]/div[1]/div[1]/div/div[1]/text()").extract_first()
        hours = response.xpath("//*[@id='taplc_attraction_detail_listing_0']/div[1]/div[2]/text()").extract_first()
        location = response.xpath("//*[@id='taplc_attraction_detail_listing_0']/div[2]/div[2]/span/text()").extract()
        if len(location) > 0:
            location = ", ".join(location).strip()
            attraction["location"] = location
        else:
            attraction["location"] = None

        attraction["name"] = title
        attraction["rating"] = rating
        attraction["number_of_reviews"] = reviews
        attraction["description"] = description
        attraction["hours"] = hours
        attraction["url"] = response.request.url

        return attraction