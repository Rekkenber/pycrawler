# pycrawlermodules
import requests
import os
import re
import json
from bs4 import BeautifulSoup

# JSON formatting
def jsonformatting(obj):
    if isinstance(obj, str):
        return obj.replace("', ", "', \n")
    elif isinstance(obj, dict):
        return {key: jsonformatting(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [jsonformatting(item) for item in obj]
    else:
        return obj

# Returns max page count
def pagecount(soup):
    paginator_div = soup.find("div", {"data-cy": "paginator"})

    # Find the second child span with data-cy="page-count" within the paginator_div
    if paginator_div:
        spans = paginator_div.findChildren("span", {"data-cy": "page-count"})
        for span in spans:
            return int((span.text)[4:])
    else:
        raise IndexError("Paginator div not found.")

# href url builder
def url_from_href(href):
    return f"https://www.jobup.ch{href}"

# Soupification into UTF-8
def prettySoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    soup.prettify()
    return soup

# JSON reader for already collected results
def JSONreader(jsonfile, printKeys=False):
    # Inits
    hash_database = []
    isFileEmpty = os.stat(jsonfile).st_size == 0
    with open(jsonfile, 'r', encoding='utf-8') as file:
        if not isFileEmpty:
            # Load already collected json results
            json_object = json.load(file)
            # Extract keys from json dictionary
            if printKeys:
                print("Collected keys:")
            for item in json_object:
                # Add keys to hash database
                key = list(item.keys())[0]
                hash_database.append(key)
                if printKeys:
                    print(key)
            return (json_object, hash_database)
        else:
            print("File empty")
            return ([], [])
        
# JSON description cleaner
def striptags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, ' ', text)