# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

import scrapy
import pickle
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
import re

class TripadvisorAttractionSpider(scrapy.Spider):
    name = 'tripadvisorattractionspider'
    allowed_domains = ['tripadvisor.com' , 'www.tripadvisor.com/Attractions']
    
    def __init__(self, *args, **kwargs):
        super(TripadvisorAttractionSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.attractions=[]
        self.destination = kwargs.get('destination')
        print(self.destination)

    def parse(self, response):
        #titles = response.css('.listing_title a::text').extract()
        #comments = response.css('.comments::text').extract()
        #print(titles)
        links = response.css('div.listing_commerce a::attr(href)').extract()

        print(links)

        #atttractions = {}

        for link in links:
            yield response.follow(link, callback=self.attraction_parse)
            

        
        #Give the extracted content row wise
#        for item in zip(titles,comments,links):
#            #create a dictionary to store the scraped info
#            number_comment = item[1].split()[0];
#            posts['title'].append(item[0])
#            posts['num_reply'].append(number_comment)
#            posts['thread_url'].append(item[2])
#            
            #yield or give the scraped info to scrapy
            #if number_comment != 'comment': #and int(number_comment) >= 5:            
                #yield response.follow(item[2], callback=self.thread_parse)

        # next_page = response.css('div.unified.pagination a::attr(href)').extract_first()
        # print(next_page)
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)

    def attraction_parse(self, response):
        attraction = {}
        
        title = response.css('#HEADING::text').extract_first()
        rating = response.xpath("//*[@id='taplc_location_detail_header_attractions_0']/div[1]/span[1]/div/div/span/@content").extract_first()
        reviews = response.xpath("//*[@id='taplc_location_detail_header_attractions_0']/div[1]/span[1]/div/a/span/text()").extract_first()
        description = response.xpath("//*[@id='taplc_location_detail_overview_attraction_0']/div/div[2]/div[2]/div[1]/div[1]/div/div[1]/text()").extract_first()
        hours = response.xpath("//*[@id='taplc_attraction_detail_listing_0']/div[1]/div[2]/text()").extract_first()
        location = response.xpath("//*[@id='taplc_attraction_detail_listing_0']/div[2]/div[2]/span/text()").extract()
        location = ", ".join(location).strip()
        # locmap = response.xpath("//*[@id='LOCATION_TAB']/div[2]/div/div[2]/div/div/div[1]").extract()
        # print(locmap)
        
        print(response.css("div.prw_rup.prw_common_static_map_no_style.staticMap").extract())

        soup = BeautifulSoup(response.xpath("//*[@id='LOCATION_TAB']").extract_first(), "html.parser")
        latlng = soup.find_all('div',class_='dynamicMap')
        print(latlng)

        # map_url = response.xpath("//*[@id='taplc_location_detail_overview_attraction_0']/div/div[2]/div[1]/div/img/@src").extract()
        # print(map_url)
        attraction["name"] = title
        attraction["rating"] = rating
        attraction["number_of_reviews"] = reviews
        attraction["description"] = description
        attraction["hours"] = hours
        attraction["location"] = location

        self.attractions.append(attraction)
        # print(self.attractions)
        #return title