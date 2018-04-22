# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class AttractioncrawlerSpider(CrawlSpider):
    # name = 'attractioncrawler'
    # allowed_domains = ['https://www.tripadvisor.com']
    # start_urls = ['http://https://www.tripadvisor.com/']

    # rules = (
    #     Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    # )

    # def parse_item(self, response):
    #     i = {}
    #     #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
    #     #i['name'] = response.xpath('//div[@id="name"]').extract()
    #     #i['description'] = response.xpath('//div[@id="description"]').extract()
    #     return i


    name = 'attractioncrawler'
    allowed_domains = ['tripadvisor.com' , 'www.tripadvisor.com/Attractions']
    #start_urls = ["https://www.tripadvisor.com/Attractions-g60763-Activities-New_York_City_New_York.html"]

    def __init__(self, *args, **kwargs):
        super(AttractioncrawlerSpider, self).__init__(*args, **kwargs)
        #self.start_urls = [start_url]
        #self.attractions=[]
        self.url = kwargs.get('url')
        self.start_urls = [self.url]
        self.number_of_attractions = 0
        #self.start_urls = kwargs.get('url')
        #start_urls = [self.start_url]
        #print(self.start_urls)

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

        #rating = response.xpath("//*[@id='taplc_location_detail_header_attractions_0']/div[1]/span[1]/div/div/span/@content").extract_first()
        #reviews = response.xpath("//*[@id='taplc_location_detail_header_attractions_0']/div[1]/span[1]/div/a/span/text()").extract_first()
        description = response.xpath("//*[@id='taplc_location_detail_overview_attraction_0']/div/div[2]/div[2]/div[1]/div[1]/div/div[1]/text()").extract_first()
        hours = response.xpath("//*[@id='taplc_attraction_detail_listing_0']/div[1]/div[2]/text()").extract_first()
        location = response.xpath("//*[@id='taplc_attraction_detail_listing_0']/div[2]/div[2]/span/text()").extract()
        location = ", ".join(location).strip()
        # locmap = response.xpath("//*[@id='LOCATION_TAB']/div[2]/div/div[2]/div/div/div[1]").extract()
        # print(locmap)
        
        #print(response.css("div.prw_rup.prw_common_static_map_no_style.staticMap").extract())

        #soup = BeautifulSoup(response.xpath("//*[@id='LOCATION_TAB']").extract_first(), "html.parser")
        #latlng = soup.find_all('div',class_='dynamicMap')
        #print(latlng)

        # map_url = response.xpath("//*[@id='taplc_location_detail_overview_attraction_0']/div/div[2]/div[1]/div/img/@src").extract()
        # print(map_url)
        attraction["name"] = title
        attraction["rating"] = rating
        attraction["number_of_reviews"] = reviews
        attraction["description"] = description
        attraction["hours"] = hours
        attraction["location"] = location

        #self.attractions.append(attraction)
        #print(attraction)
        return attraction