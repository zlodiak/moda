import requests
import os
import lxml.html
import urllib
import re


def get_doc(url):
    try:
        req = requests.get(url)
    except requests.exceptions.ConnectionError as exc:
        print('A Connection error occurred. ', exc)
    else:
        doc_html = req.text
        #print(doc_html)
        doc_obj = lxml.html.document_fromstring(doc_html)        
        return doc_html, doc_obj
        
        
def record_xml_to_file(xml, fileName='xml.xml'):
    xmlPretty = lxml.etree.tounicode(xml, pretty_print=True)
    print(xmlPretty, 'quantity items: ', itemsQuantity)
    
    try:
        with open(fileName, "wt") as file:
            file.write(xmlPretty)
    except OSError as exc:
        return False
    else:
        return True


def check_catalog_exist(data_catalog_name):
    if os.path.exists(data_catalog_name):
        return True
    else:
        return False


def create_catalog(data_catalog_name):
    try: 
        os.mkdir(data_catalog_name)
    except OSError as exc:
        return False
    else:
        return True


def clean_catalog(data_catalog_name):
    try:
        for item in os.listdir(data_catalog_name):
            item = os.path.join(data_catalog_name, item)
            if os.path.isfile(item):
                os.remove(item) 
            else:
                os.rmdir(item)
    except OSError as exc: 
        return False
    else:
        return True


def secure_chars(word):
    replace_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '-' , ' ', '!', ';']
    if type(word) == str:
        for char in replace_chars:
            word = word.lower().strip().replace(char, '_')
    else:
        print('warning! not str')

    return str(word)


def download_image(path, catalog):
    img = urllib.request.urlopen(path).read()

    search = re.search('(.+)\/(.+)$', path)
    name = search.group(2)

    fullPath = os.path.join(catalog, name)

    print(fullPath)#

    with open(fullPath, "wb") as f:
        f.write(img)        
    
