from bs4 import BeautifulSoup
import sys
import requests
import json

def build_css_selector(important, ignore):
    """ build css selector string for beautifulsoup to parse pertinent elements
    important - array of words to look for elements with a class that includes the word in important
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


def check_ignore_in_string(string, ignore):
    """ check if the string provided contains a word in the array ignore
    string - string to check 
    ignore - array of words to check string for
    Returns: True - string does not include any words in ignore.
             False - string includes at least one word in ignore.
    """
    for word in ignore:
        if ignore in string:
            return False
    return True


def scrape_page(url):
    """ scrape url given and returns title of product, price, previous price, styles, photoURL
    """
    ignore = ["additional", "related", "similar", "cart"]
    important = ["price", "colors"]
    selector = build_css_selector(important, ignore)


    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    prices_possibilites = soup.select(selector)
    
    price_narrow = []
    for price in prices_possibilites:
        for parent in price.parents:
            if 'class' in parent:
                # if parent class has something from ignore array, break out of looping parents
                if not check_ignore_in_string(parent['class'], ignore):
                    break
        else:
            price_narrow.append(price)


    for price in price_narrow:
        # print(price)
        print(price.text)
        print('~~~~~~~~~~~~')   
        
        
    result = {
        "product_title": soup.title.string
    }

    return json.dumps(result)

if __name__ == "__main__":
    print(scrape_page(sys.argv[1]))