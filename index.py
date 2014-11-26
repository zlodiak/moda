import lxml.html
import lxml.etree
import my_utils
import os
import my_extras
import pprint
import re
import debug


def get_categories_urls(doc_obj, baseUrl):
    firstUrlsList = []
    li = doc_obj.xpath('//nav[@id="LandingLeft"]/ul/li[position() <= 2]')
    if len(li):
        catalogSection = [elem for elem in li]
        #print(catalogSection)

        if len(catalogSection):
            for elem in catalogSection:
                url = elem.xpath('ul/li/a/@href')
                for link in url:
                    href = str(baseUrl)[:-1] + str(link)
                    firstUrlsList.append(href)
                    
            return firstUrlsList


def get_goods_pages_urls(firstUrlsList, baseUrl):
    allUrlsList = []
    
    firstUrlsList = ['http://en.modagram.com/women/dresses/cat/4']#
    for url in firstUrlsList:
        req = my_utils.get_doc(url)
        doc_html, doc_obj = req
        href = doc_obj.xpath('//nav[@class="Paging"][position() = 1]/a[not(@rel = "next")][position() = last()]/@href')
        if len(href):
            search = re.search('(.*?).page=(\d+)$', str(href[0]))
            base_path = search.group(1)
            page_num = search.group(2)
            goods_pages_list = []
            [goods_pages_list.append(baseUrl + base_path + '?page=' + str(i)) for i in range(1, int(page_num) + 1)]

        [allUrlsList.append(url) for url in goods_pages_list]
        
    return allUrlsList
        

def get_goods_urls(allUrlsList, baseUrl):
    goods_urls = [] 
    
    for url in allUrlsList:
        req = my_utils.get_doc(url)
        doc_html, doc_obj = req           
        goods_url = doc_obj.xpath('//section[@id="ProductList"]/ol/li/a/@href')
        if len(goods_url):
            for href in goods_url:
                goods_urls.append(baseUrl + href)

    return goods_urls


def get_goods_data_dict(goods_urls):
    goods_data_dict = {}
    ii = 0#
    
    for url in goods_urls:
        ii = ii + 1#
        if ii > 25: break#
        req = my_utils.get_doc(url)
        doc_html, doc_obj = req

        base_texts_query = doc_obj.xpath('//section[@id="ProductBuyOptions"]')
        if len(base_texts_query):
            title = base_texts_query[0].xpath('h1[@itemprop="name"]/text()')
            if len(title):
                title = title[0]
                #print(title[0])#

            price = base_texts_query[0].xpath('div[@class="Prices"]/meta[position() = last()]/@content')
            if len(price):
                price = price[0]
                #print(price)#

            currency = base_texts_query[0].xpath('div[@class="Prices"]/meta[@itemprop="currency"]/@content')
            if len(currency):
                currency = currency[0]
                #print(currency, end='\n\n')#

            colors = []
            colors_raw = base_texts_query[0].xpath('div[@class="ProductColor"]/a/@title')
            if len(colors_raw):
                [colors.append(color) for color in colors_raw]
                #print(colors)#

            sizes = []
            sizes_raw = base_texts_query[0].xpath('div[@class="ProductSize"]/a/text()')
            if len(sizes_raw):
                [sizes.append(size) for size in sizes_raw]
                #print(sizes)#

            details = {}
            base_details_query = doc_obj.xpath('//section[@id="ProductInfo"]/div[contains(concat(" ", normalize-space(@class), " "), " TabItem ")]')
            if len(base_details_query):
                base_details_query = base_details_query[0].xpath('//p/strong')
                if len(base_details_query):
                    for dict_title in base_details_query:
                        p = dict_title.getparent()
                        p = p.getnext()
                        #print(dict_title, dict_title.text, p, p.text, '-----p')#
                        desc = []
                        i = 0
                        while p is not None and not p.xpath('.//strong'):
                            desc.append(p.text)
                            p = p.getnext()

                        if dict_title.text != ':':
                            details[dict_title.text] = desc

                #pprint.pprint(details)#
                        

            photos_big_list = []
            photos_raw = doc_obj.xpath('//section[@id="ProductPhotos"]//a/img/@src')
            if len(photos_raw):
                for photo in photos_raw:
                    photo_big = re.sub('\/3\/', '/2/', photo)
                    photos_big_list.append(photo_big)
                #pprint.pprint(photos_big_list)#


            path_list = []
            path_raw = doc_obj.xpath('//div[@class="selectivePath"]/a/text()')
            if len(path_raw):
                #[path_list.append(my_utils.secure_chars(path.strip())) for path in path_raw]
                [path_list.append(path.strip()) for path in path_raw]

            #pprint.pprint(path_list)#
            print('0000000')#

        goods_data_dict[title] = {
                                    'url': url,
                                    'price': price,
                                    'currency': currency,
                                    'colors': colors,
                                    'sizes': sizes,
                                    'details': details,
                                    'photos': photos_big_list,
                                    'paths': path_list
        }

    return goods_data_dict


def construct_catalog_tree(goods_data_dict):
    errors = 0
    
    try:
        os.chdir('data')
    except OSError as exc:
        print('error change catalog')
    else:
        current_catalog = os.getcwd()

        for value in goods_data_dict.values():
            #print(value['paths'])#
            current_catalog_new = current_catalog
            for path in value['paths']:
                #print('\t', path)#
                current_catalog_new = os.path.join(current_catalog_new, path)
                #print('\t', current_catalog_new)#

                if not os.path.exists(current_catalog_new):
                    if not my_utils.create_catalog(current_catalog_new):
                        print('\t\terror catalog create')
                        errors = errors + 1
                    else:
                        print('\t\t ok')
                else:
                    print('\t\t EXIST')

    if errors:
        return False
    else:
        return True
   

def fill_catalog_tree(goods_data_dict):
    errors = 0
    current_catalog = os.path.join(os.getcwd(), 'data')
    parent = lxml.etree.Element('data')
    #ii = 0#
    
    for key, value in goods_data_dict.items():
        #ii = ii + 1#
        #if ii > 2: break#
        current_catalog_new = current_catalog
        for val in value['paths']:
            current_catalog_new = os.path.join(current_catalog_new, val)

        current_catalog_new = os.path.join(current_catalog_new, key)

        if not my_utils.create_catalog(current_catalog_new):
            print('\t\terror catalog create')
            errors = errors + 1
        else:
            for img_path in value['photos']:
                my_utils.download_image(img_path, current_catalog_new)

            child_item = my_extras.construct_child_item(current_catalog_new=current_catalog_new,
                                                        key=key,
                                                        value=value)

            parent.append(child_item)
            
    if not errors:
        return parent


def construct_xml_node():
    pass


def record_xml_to_file(xml, fileName='xml.xml', xml_declaration='<?xml version="1.0" encoding="utf-8"?>'):
    xmlPretty = lxml.etree.tounicode(xml, pretty_print=True)
    print(xmlPretty)

    try:
        with open(fileName, "wt") as file:
            #file.write(xmlPretty)
            file.write(bytes(lxml.etree.tounicode(xml, doctype=xml_declaration), 'UTF-8')) 
    except OSError as exc:
        print('Error record. ', exc)
    else:
        return True

    
            
if __name__ == "__main__":
    '''
    #конфиг
    baseUrl = 'http://en.modagram.com/'
    data_catalog_name = 'data'

    #готовим каталог для данных
    catalog_exist = my_utils.check_catalog_exist(data_catalog_name)
    if catalog_exist:
        print('Catalog already exists\n')
        clean = my_utils.clean_catalog(data_catalog_name)
        if not clean:
            print('Error clean catalog.')
    else:
        create = my_utils.create_catalog(data_catalog_name)
        if not create:
            print('Error. Catalog is not ready.')

    #получаем список первых страниц для каждой категории
    req = my_utils.get_doc(baseUrl)
    doc_html, doc_obj = req

    firstUrlsList = get_categories_urls(doc_obj, baseUrl)
    #pprint.pprint(firstUrlsList)

    #gполучаем набор ссылок для всех страниц каждой категории
    allUrlsList = get_goods_pages_urls(firstUrlsList, baseUrl)
    #pprint.pprint(allUrlsList)

    #получаем набор ссылок на страницы карточек товара
    goods_urls = get_goods_urls(allUrlsList, baseUrl)
    #pprint.pprint(goods_urls)

    #парсим каждую страницу карточки товара
    goods_data_dict = get_goods_data_dict(goods_urls)
    
    #goods_data_dict = debug.goods_data_dict#
    pprint.pprint(goods_data_dict)

    #построим дерево каталогов
    catalog_tree = construct_catalog_tree(goods_data_dict)
    #print(catalog_tree)
'''
    catalog_tree = True#
    goods_data_dict = debug.goods_data_dict#
    #заполняем созданные каталоги

    if not catalog_tree:
        print('error catalog tree create')
    else:
        xml = fill_catalog_tree(goods_data_dict)

        if type(xml) == lxml.etree._Element:
            rec_xml = record_xml_to_file(xml)
            if rec_xml:
                print('record xml to file successfull')
            else:
                print('record xml to file failed')
    


