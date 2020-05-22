# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import sys
import requests
import json
import re

def build_css_selector(important, ignore):
    """ build css selector string for beautifulsoup to parse pertinent elements
    Params: important - array of words to look for elements with a class that includes the word in important
            ignore - array of words to ignore elements with this word in it's class
    Returns: selector string for searching elements that include important class and don't have ignore class
    """
    attributes = ['class', 'data-at']
    selector = ""
    for word in important:
        for attr in attributes:
            selector += "[" + attr +"*='" + word + "']"
            for ignore_word in ignore:
                selector += ":not([class*='" + ignore_word + "'])"
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


def check_parents(element, ignore):
    """ for each of element's parents, check if the parent's class includes a word in ignore
    Params: element - soup element to check parents of
            ignore - array of words to check if element's parent's class contains
    Returns: True - none of the parents' classes include a word from ignore
             False - at least one of the parents' classes include a word from ignore array
    """
    print(element.text)
    for parent in element.parents:
        # if parent class has something from ignore array, break out of looping parents
        if parent.get('class') != None:
            print(parent['class'])
            if not check_valid_array(parent['class'], ignore):
                return False
            if not check_valid_array(parent.text, ignore):
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

def scrape_page(url):
    """ scrape url given and returns title of product, price, previous price, styles, photoURL
    Param: url - url to scrape
    Returns: json format holding title, price, prevPrice, styles, photoURL
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    ignore = ["related", "similar", "cart"]
    ignore_after = ["related", "similar", "recommended", "frequently", "add to cart"]
    price_keywords = ["price", "Price", "Pricing"]
    price_divs = soup.select(build_css_selector(price_keywords, ignore))
    print(soup.prettify())
    prevPrice, currPrice, onSale = None, None, False
    possiblePrices = set()
    for div in price_divs:
        if div.parent.get('class') == None or check_valid_array(div.parent['class'], ['cart']):
            if check_parents(div, ignore_after):
                print("found one price!", div.text)
                # find all currencies in div text replacing any space characters
                for item in re.findall("(?:[\£\$\€]{1} *[,\d]+.?\d*)", div.text.replace(u'\xa0', ' ')):
                    possiblePrices.add(item)
            else:
                break

    print('possiblePrices', possiblePrices)
    possiblePrices = list(possiblePrices)
    if len(possiblePrices) == 1:
        prevPrice = possiblePrices[0]
        currPrice = possiblePrices[0]
    elif len(possiblePrices) > 1:
        # assume on sale if 2 prices found
        onSale = True

        currency = possiblePrices[0][0]
        minPrice = float(possiblePrices[0][1:])
        maxPrice = minPrice
        for price in possiblePrices:
            value = float(price[1:])
            minPrice = min(minPrice, value)
            maxPrice = max(maxPrice, value)
        currPrice = convert_to_currency_string(minPrice, currency)
        prevPrice = convert_to_currency_string(maxPrice, currency)
        
    result = {
        "product_title": re.sub(r'[^A-Za-z0-9 ]+', '', soup.title.string),
        "prevPrice": prevPrice,
        "currPrice": currPrice,
        "onSale": onSale
    }
    return json.dumps(result)

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
