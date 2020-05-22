from bs4 import BeautifulSoup
import sys
import requests
import json

def build_css_selector(important, ignore):
    selector = ""
    for word in important:
        selector += "[class*='" + word + "']"
        for word in ignore:
            selector += ":not([class*='" + word + "'])"
        selector += ", "
  
    return selector[:-2]

def check_parent_valid(parent_class, ignore):
    for word in ignore:
        if ignore in parent_class:
            return False
    return True

def scrape_page(url):
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
                if not check_parent_valid(parent['class'], ignore):
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