# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup, Tag
import sys
import requests
import json
import re
import time
MATCH_ALL = r'.*'

def build_css_selector(important, ignore):
    """ build css selector string for beautifulsoup to parse pertinent elements
    Params: important - array of words to look for elements with a class that includes the word in important
            ignore - array of words to ignore elements with this word in it's class
    Returns: selector string for searching elements that include important class and don't have ignore class
    """
    attributes = ['class', 'data-at', 'id']
    selector = ""
    for word in important:
        for attr in attributes:
            selector += "[" + attr +"*='" + word + "']"
            for ignore_word in ignore:
                selector += ":not([" + attr + "*='" + ignore_word + "'])"
            selector += ", "
  
    return selector[:-2]


def check_valid_array(array, ignore):
    """ check if any of the words in ignore are contains in any of the strings in array
    Params: array - array of strings to check 
            ignore - array of words to avoid in array
    Returns: True - none of the strings in array include the any of the words in ignore
             False - at least one of the strings in array include a word in ignore.
    """
    for word in array:
        for ignore_word in ignore:
            if ignore_word in word:
                return False
    return True


def check_up_to(element, check_type, up_to, ignore):
    """ for each of element's parents, check if the parent's class includes a word in ignore
    Params: element - soup element to check parents of
            ignore - array of words to check if element's parent's class contains
    Returns: True - none of the parents' classes include a word from ignore
             False - at least one of the parents' classes include a word from ignore array
    """
    print(element.text)
    if check_type == "parents":
        for parent in element.parents:
            if parent == up_to:
                return True
            # if parent class has something from ignore array, break out of looping parents
            if parent.get('class') != None:
                print(parent['class'])
                if not check_valid_array(parent['class'], ignore):
                    return False
                if not check_valid_array(parent.text, ignore):
                    return False
    elif check_type == "previous":
        for prev in element.previous_elements:
            if prev == up_to:
                return True
            # if parent class has something from ignore array, break out of looping parents
            if isinstance(prev, Tag) and prev.get('class') != None:
                print(prev['class'])
                if not check_valid_array(prev['class'], ignore):
                    return False
                if not check_valid_array(prev.text, ignore):
                    return False
    return True

def convert_to_currency_string(price, currency):
    """Combine price to correctly formatted currency string
    Params: price - price value to convert to string
            currency - the currency of the price given
    Returns: Properly formatted price string
    """
    currPrice = currency + str(price)
    remaining = 6 - len(currPrice)
    currPrice += '0' * remaining
    return currPrice

def set_price(currency, priceA, priceB):
    prevPrice = min(priceA, priceB)
    currPrice = max(priceA, priceB)
    return (convert_to_currency_string(prevPrice, currency), convert_to_currency_string(currPrice, currency))

def scrape_page(url):
    """ scrape url given and returns title of product, price, previous price, styles, photoURL
    Param: url - url to scrape
    Returns: json format holding title, price, prevPrice, styles, photoURL
    """
    style = ["style", "variation", "version"]
    img = ["img", "carousel"]
    page = requests.get(url,headers={"User-Agent":"Defined"})
    time.sleep(5)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.prettify
    # page = '<span id="priceblock_ourprice" class="a-size-medium a-color-price priceBlockBuyingPriceString">$11.97</span>'
    # soup = BeautifulSoup(page, 'html.parser')
    ignore = ["related", "similar", "cart"]
    ignore_after = ["related", "similar", "recommended", "frequently", "add to cart"]
    price_keywords = ['Price', 'price', 'Pricing', 'pricing']
    price_divs = soup.select(build_css_selector(price_keywords, ignore))
    # price_divs = soup.find(text=like('$'))
    # price_divs = find_by_text(soup, ['$'], 'div')
    # price_divs = soup.findAll(lambda tag:tag.name=="span" and "$" in tag.text)
    # pattern = re.compile('$')
    # price_divs = soup.findAll(text=pattern)
 
    prevPrice, currPrice, onSale = None, None, False
    previousDivParent = None
    foundPrices = {}
    for div in price_divs:
        print(div)
        if div.parent.get('class') == None or check_valid_array(div.parent['class'], ['cart']):
            # if check_up_to(div, "previous", previousDivParent, ignore_after):
            # find all currencies in div text replacing any space characters
            possPrices = re.findall("(?:[\£\$\€]{1} *[,\d]+.?\d*)", div.text.replace(u'\xa0', ' '))
            print('prices found:', possPrices)
            if len(possPrices) == 2:
                currPrice, prevPrice = set_price(possPrices[0][0], float(possPrices[0][1:]), float(possPrices[1][1:]))
                break
            elif len(possPrices) == 1:
                if div.parent not in foundPrices:
                    foundPrices[div.parent] = possPrices[0]
                    currPrice = convert_to_currency_string(float(possPrices[0][1:]), possPrices[0][0])
                    prevPrice = currPrice
                else:
                    currPrice, prevPrice = set_price(possPrices[0][0], float(possPrices[0][1:]), float(foundPrices[div.parent][1:]))
                    break
        previousDivParent = div.parent

    result = {
        "product_title": re.sub(r'[^A-Za-z0-9 ]+', '', soup.title.string),
        "prevPrice": prevPrice,
        "currPrice": currPrice,
        "onSale": onSale
    }
    return json.dumps(result)


def like(string):
    """
    Return a compiled regular expression that matches the given
    string with any prefix and postfix, e.g. if string = "hello",
    the returned regex matches r".*hello.*"
    """
    string_ = string
    if not isinstance(string_, str):
        string_ = str(string_)
    regex = MATCH_ALL + re.escape(string_) + MATCH_ALL
    return re.compile(regex, flags=re.DOTALL)


def find_by_text(soup, text, tag):
    """
    Find the tag in soup that matches all provided kwargs, and contains the
    text.

    If no match is found, return None.
    If more than one match is found, raise ValueError.
    """
    elements = soup.find_all(tag)
    matches = []
    for element in elements:
        for txt in text:
            if element.find(text=like(txt)):
                matches.append(element)
                break
    return matches

    
if __name__ == "__main__":
    url = sys.argv[1]
    print(scrape_page(url.split('?')[0]))
    

def scrape_page2(url):
    """ scrape url given and returns title of product, price, previous price, styles, photoURL
    """
    ignore = ["additional", "related", "similar", "cart"]
    important = ["price", "colors"]
    selector = build_css_selector(important, ignore)


    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    content = soup.find_all('div')
    price_narrow = []
    for div in content:
        print(div.text)
        if 'related' in div.text:
            break
        possibilities = div.select(selector)
        for parent in possibii.parents:
            if 'class' in parent:
                # if parent class has something from ignore array, break out of looping parents
                if not check_ignore_in_string(parent['class'], ignore):
                    break
        else:
            price_narrow.append(price)
