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
    selector = ""
    for word in important:
        selector += "[class*='" + word + "']"
        for word in ignore:
            selector += ":not([class*='" + word + "'])"
        selector += ", "
  
    return selector[:-2]


def check_ignore_in_string(array, ignore):
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


def check_parents_class(element, ignore):
    """ for each of element's parents, check if the parent's class includes a word in ignore
    Params: element - soup element to check parents of
            ignore - array of words to check if element's parent's class contains
    Returns: True - none of the parents' classes include a word from ignore
             False - at least one of the parents' classes include a word from ignore array
    """
    for parent in element.parents:
        # if parent class has something from ignore array, break out of looping parents
        if parent.get('class') != None:
            if not check_ignore_in_string(parent['class'], ignore):
                return False
    return True

def scrape_page(url):
    """ scrape url given and returns title of product, price, previous price, styles, photoURL
    Param: url - url to scrape
    Returns: json format holding title, price, prevPrice, styles, photoURL
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    ignore = ["additional", "related", "similar", "cart"]
    ignore_after = ["additional", "related", "similar"]
    price_keywords = ["price"]
    prices_possibilites = soup.select(build_css_selector(price_keywords, ignore))
    prevPrice, currPrice = "", ""
    for price in prices_possibilites:
        if check_parents_class(price, ignore_after):
            currency = re.findall("(?:[\£\$\€]{1}[,\d]+.?\d*)", price.text)
            # for now only does for USD currency
            if len(currency) > 1: # on sale theoretically
                if currency[0] <= currency[1]:
                    prevPrice = currency[1]
                    currPrice = currency[0]
                else:
                    prevPrice = currency[0]
                    currPrice = currency[1]
        else:
            break

        
    result = {
        "product_title": soup.title.string,
        "prevPrice": prevPrice,
        "currPrice": currPrice
    }

    return json.dumps(result)


if __name__ == "__main__":
    print(scrape_page(sys.argv[1]))
    # string =['related-time', 'related-products-wrapper', 'product-section']
    # ignore = ["additional", "related", "similar"]
    # print(check_ignore_in_string(string, ignore))

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
