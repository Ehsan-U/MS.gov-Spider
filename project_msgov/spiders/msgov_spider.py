import json
import scrapy
from ..items import ProjectMsgovItem
from scrapy.loader import ItemLoader


class MsgovSpider(scrapy.Spider):
    name = 'msgov_spider'
    allowed_domains = ['ms.gov']
    mappings = {
        'amendment_files':['amendment','renewal','extension'],
        'contract_files':['contract','signed','executed','agreement'],
        'pricing_files':['price','pricing'],
    }

    def start_requests(self):
        url = 'https://www.ms.gov/dfa/contract_bid_search/Contract/ContractData?AppId=1'
        payload = self.prepare_payload()
        yield scrapy.FormRequest(url,formdata=payload, callback=self.parse)

    def parse(self, response):
        body = response.body
        data = json.loads(body)
        for contract in data.get("aaData")[:5]:
            id_ = contract.get("ContractID")
            url = f'https://www.ms.gov/dfa/contract_bid_search/Contract/Details/{id_}?AppId=1'
            yield scrapy.Request(url, callback=self.parse_contract)
    
    def parse_contract(self, response):
        sel = scrapy.Selector(text=response.text)

        suppliers = sel.xpath("//span[@id='lblPrimaryVendor']/text()").get()
        title = sel.xpath("//span[@id='lblContractDescription']/text()").get()
        contract_number = sel.xpath("//span[@id='lblObjectId']/text()").get()
        effective,expiration = sel.xpath("//span[@id='lblContractValidityDates']/text()").get().split('-')
        source_url = response.url
        buyer_contacts = {
            "name":sel.xpath("//span[@id='lblContactName']/text()").get(),
            "email":sel.xpath("//span[@id='lblContactEmail']/text()").get(),
            "phone":sel.xpath("//span[@id='lblContactPhone']/text()").get()
        }
        supplier_contacts = {"address":"".join(sel.xpath("//span[@id='lblPrimaryVendorAddress']/text()").getall())}
        contract_type,cooperative_language = self.decide_type(sel)
        scraped_offerings_list = sel.xpath("//span[@id='lblContractItems']/following-sibling::table/tbody/tr[position()>2]/td[5]/text()").getall()
        category_data = {
            'nigp':sel.xpath("//span[@id='lblContractItems']/following-sibling::table/tbody/tr[position()>2]/td[3]/text()").getall()
        }

        loader = ItemLoader(item=ProjectMsgovItem(), response=response, selector=sel)
        loader.add_value("buyer_lead_agency", "State of Mississippi")
        loader.add_value("source_key", "state-of-mississippi")
        loader.add_value("buyer_lead_agency_state", "MS",)
        loader.add_value("service_area_national", False)
        loader.add_value("service_area_state", ["MS"])
        loader.add_value("suppliers", suppliers)
        loader.add_value("title", title)
        loader.add_value("contract_number", contract_number)
        loader.add_value("effective", effective)
        loader.add_value("expiration", expiration)
        loader.add_value("source_url", source_url)
        loader.add_value("buyer_contacts", buyer_contacts)
        loader.add_value("supplier_contacts", supplier_contacts)
        loader.add_value("contract_type", contract_type)
        loader.add_value("cooperative_language", cooperative_language)
        files = self.decide_filetype(sel)
        for k,val in files.items():
            loader.add_value(k, val)
        loader.add_value("scraped_offerings_list", scraped_offerings_list)
        loader.add_value("category_data", category_data)

        yield loader.load_item()

    def decide_type(self, sel):
        contract_category = sel.xpath("//span[@id='lblContractCategory']/text()").get()
        if contract_category:
            contract_category = contract_category.lower().strip()
            list1 = ['optfm-cooperative','its-epl','optfm-comp','optfm-negc','pscrb-p1']
            list2 = ['its-cp1','its-exemption','pscrb-preapproved']
            if contract_category in list1:
                contract_type = 'competitively_bid_contract'
                cooperative_language = True
            elif contract_category in list2:
                contract_type = 'sole_source_justification'
                cooperative_language = False
            # 'optfm-p1' ignore
            else:
                contract_type = ''
                cooperative_language = ''
        else:
            contract_type = ''
            cooperative_language = ''

        return contract_type,cooperative_language

    def decide_filetype(self, sel):
        files = {
            'contract_files':[],
            'amendment_files':[],
            'pricing_files':[],
            'other_docs_files':[]
        }
        for f in sel.xpath("//span[@id='lblAttachments']/a"):
            f_text = f.xpath("./text()").get()
            f_link = f.xpath("./@href").get()
            type_found = False
            for k,vals in self.mappings.items():
                for v in vals:
                    if v in f_text.lower():
                        files[k].append({'name':f_text,"url":f_link})
                        type_found = True
            if not type_found:     
                files['other_docs_files'].append(f)
        return files        

    def prepare_payload(self):
        payload = {}
        rawString = 'sEcho=2&iColumns=8&sColumns=%2C%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=9999&mDataProp_0=ContractNumber&bSortable_0=true&mDataProp_1=ObjectID&bSortable_1=true&mDataProp_2=PrimaryVendor&bSortable_2=true&mDataProp_3=ShortDescription&bSortable_3=true&mDataProp_4=StartDate&bSortable_4=true&mDataProp_5=EndDate&bSortable_5=true&mDataProp_6=PCardEnabled&bSortable_6=true&mDataProp_7=7&bSortable_7=false&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1'
        for item in rawString.split('&'):
            item = item.split("=")
            payload[item[0]] = item[-1]
        return payload
