import lxml.html
import lxml.etree
import my_utils
import os

def construct_child_item(   current_catalog_new,
                            key,
                            value):
    child_item = lxml.etree.Element('item' , href=current_catalog_new)

    child_title = lxml.etree.Element('title')
    child_title.text = key    

    child_price = lxml.etree.Element('price')
    child_price.text = value['price']

    child_url = lxml.etree.Element('url')
    child_url.text = value['url']    

    child_currency = lxml.etree.Element('currency')
    child_currency.text = value['currency']

    child_colors = lxml.etree.Element('colors')
    for color in value['colors']:
        child_color = lxml.etree.Element('color')
        child_color.text = color
        child_colors.append(child_color)

    child_sizes = lxml.etree.Element('sizes')
    for size in value['sizes']:
        child_size = lxml.etree.Element('size')
        child_size.text = size
        child_sizes.append(child_size)

    child_photos_web = lxml.etree.Element('photos_web')
    for photo in value['photos']:
        child_photo = lxml.etree.Element('photo')
        child_photo.text = photo
        child_photos_web.append(child_photo)

    child_details = lxml.etree.Element('details')
    for detail, desc in value['details'].items():
        elem = str(my_utils.secure_chars(detail))
        child_detail = lxml.etree.Element(elem)
        prop = ''
        for val in desc:
            if type(val) == str:
                prop = prop + val + ' '
                    
        child_detail.text = prop
        child_details.append(child_detail)   

    child_item.append(child_details)
    child_item.append(child_sizes)
    child_item.append(child_colors)
    child_item.append(child_title)
    child_item.append(child_price)
    child_item.append(child_url)
    child_item.append(child_currency)

    return child_item
