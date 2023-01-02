# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime
from isodate import parse_datetime
import scrapy
from itemloaders.processors import MapCompose,TakeFirst,Join

def cleanText(string):
    if type(string) == dict:
        address = string['address'].replace(u"\xa0",u'').strip()
        string['address'] = address
        return string
    else:
        string = string.strip().replace(u"\xa0",u'').strip()
    return string
    
def isoformat(string):
    isoformatted = parse_datetime(datetime.datetime.strptime(string.strip(), "%m/%d/%Y").isoformat())
    return isoformatted

def handle_files(iterr):
    if iterr:
        pass
    else:
        iterr = ''
    return iterr

def handle_category(dictt):
    if dictt['nigp']:
        pass
    else: 
        dictt = ''
    return dictt

class ProjectMsgovItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    buyer_lead_agency = scrapy.Field(
            output_processor = TakeFirst()
    )
    source_key = scrapy.Field(
            output_processor = TakeFirst()
    )
    buyer_lead_agency_state = scrapy.Field(
            output_processor = TakeFirst()
    )
    service_area_national = scrapy.Field(
            output_processor = TakeFirst()
    )
    service_area_state = scrapy.Field(
            # output_processor = TakeFirst()
    )
    suppliers = scrapy.Field(
            input_processor = MapCompose(cleanText),
            output_processor = TakeFirst()
        )
    title = scrapy.Field(
            input_processor = MapCompose(cleanText),
            output_processor = TakeFirst()
        )
    contract_number = scrapy.Field(
            input_processor = MapCompose(cleanText),
            output_processor = TakeFirst()
        )
    effective = scrapy.Field(
            input_processor = MapCompose(cleanText,isoformat),
            output_processor = TakeFirst()
        )
    expiration = scrapy.Field(
            input_processor = MapCompose(cleanText, isoformat),
            output_processor = TakeFirst()
        )
    source_url = scrapy.Field(
            input_processor = MapCompose(cleanText),
            output_processor = TakeFirst()
        )
    buyer_contacts = scrapy.Field(
            output_processor = TakeFirst()
    )
    supplier_contacts = scrapy.Field(
            input_processor = MapCompose(cleanText),
        )
    contract_type = scrapy.Field(
            output_processor = TakeFirst()
    )
    cooperative_language = scrapy.Field(
            output_processor = TakeFirst()
    )
    contract_files = scrapy.Field(
            input_processor = MapCompose(handle_files),
        )
    amendment_files = scrapy.Field(
            input_processor = MapCompose(handle_files),
        )
    pricing_files = scrapy.Field(
            input_processor = MapCompose(handle_files),
        )
    other_docs_files = scrapy.Field(
            input_processor = MapCompose(handle_files),
        )
    scraped_offerings_list = scrapy.Field(
            input_processor = MapCompose(handle_files),
        )
    category_data = scrapy.Field(
            input_processor = MapCompose(handle_category),
        )

