import time
import random
import json
    # pycrawlermodules.py function imports
from pycrawlermodules import jsonformatting, pagecount, url_from_href, prettySoup, JSONreader, striptags

# Phase 1: ___ URL MEGAPARSER ___
# proof-of-concept crawler target: jobup.ch
# Data integrity checks: 
#   - JSON "description" value matching the following regexp `"description": ".{1,500}",` should be investigated for sources of scraping errors
#   - Scraped posts with dynamically/custom content offer or redirections to content offer may pose an issue

# Phase 1 completion requirements:
# TODO: format json result into NoSQL Amazon DynamoDB entries possibly
# TODO: lambda expression the whole thingie to run once every xx minutes

# url paging format: https://www.jobup.ch/fr/emplois/informatique-telecommunications/?page=XXX&term=

# Initialize collected hash database & json_object
json_filename = 'jobresults.json'
json_tuple = JSONreader(json_filename, printKeys=True)
json_object, hash_database = json_tuple[0], json_tuple[1]

# Initialize relevant continue/skip variables
isCrawled = False
crawlCount = 0
endCrawlCount = 5

# HTML page soupification
page_current = 0
url = f"https://www.jobup.ch/fr/emplois/informatique-telecommunications/?page=1&sort-by=date&term="
soup = prettySoup(url)

# Performance tracker
start_time = time.time()

# Fetch max page count
page_count = pagecount(soup)
print(f"Page count: {str(page_count)}. Time: {time.time() - start_time}s.")

# Visual control block for fetched page result
""" with open("result.txt", "w", encoding='utf-8') as file:
    for line in soup:
        file.write(str(line))
"""

# Loop through pages until a crawled hash is found or until all pages are crawled
while ((not isCrawled) and (not page_current == page_count)):
    # Increment page count
    page_current += 1
    print(f"Parsing page {page_current}")
    print(f"IsCrawled: {isCrawled}")

    # Don't double fetch first page
    if not page_current == 1:
        page_str = f"page={str(page_current)}&"
        url = f"https://www.jobup.ch/fr/emplois/informatique-telecommunications/?{page_str}sort-by=date&term="
        soup = prettySoup(url)

    # Target relevant job offer blocks by div params
    target_divs = soup.find_all("div", {"data-feat": ["searched_jobs", "boosted_jobs"]})

    # Div href fetching
    divcount = 0
    hrefs = []
    for div in target_divs:
        divcount += 1
        # Find links to individual job offers
        job_link = div.find("a", {"data-cy": "job-link"})
        if job_link:
            # Get & append href attribute value
            href_value = job_link.get("href")
            hrefs.append(href_value)
        else:
            print("Job link not found.")

    # Individual job offer crawling & parsing
    hrefcount = 0
    for href in hrefs:
        # Isolate hash to use as unique key
        dyna_hash = href[19:55]
        # Check for existence of key before crawl
        if dyna_hash in hash_database:
            print(f"Hash: {dyna_hash} already crawled. Skipping.")
            # Increment crawl count, abort if endCrawlCount condition is met
            crawlCount += 1
            if crawlCount == endCrawlCount: 
                isCrawled = True
                break
            continue
        # Increment count in case of existence
        hrefcount += 1
        # Add key to hash_database
        hash_database.append(dyna_hash)
        # HTML page soupification
        dyna_soup = prettySoup(url_from_href(href))

        # Target relevant job offer text by script params
        script_tags = dyna_soup.find_all('script', type='application/ld+json')

        # Extract text content inside the script tag and format it into a json file
        if len(script_tags) >= 2:
            json_content = script_tags[1].string
            # Try to load json content & append
            try:
                json_payload = json.loads(json_content)
                # Modify json payload to include relevant fields: link + description without html tags
                json_payload[0]["jobLink"] = f"https://www.jobup.ch/fr/emplois/detail/{json_payload[0]["identifier"]["value"]}/"
                json_payload[0]["description_LLM"] = striptags(json_payload[0]["description"])
                json_object.append({dyna_hash: jsonformatting(json_payload)})
            except (json.JSONDecodeError, TypeError) as e:
                # Error handling for when page format is loaded from external site, etc...
                print("Error parsing JSON:", e)
                print("Ignoring invalid entry, continuing the crawl...")
                hrefcount -= 1
                continue
        else:
            print("Script tag not found.")

        # Performance tracker: individual job offers crawl time + sleep
        print(f"Count: {hrefcount}. Hash: {dyna_hash}. Time: {time.time() - start_time}s.")
        time.sleep(random.uniform(2,6))

# Dump into json_object
with open(json_filename, "w", encoding='utf-8') as file:
    json.dump(json_object, file, ensure_ascii=False, indent=4)
    print(f"Writing done. \n# of new entries: {(page_current - 1)*20 + hrefcount}. Total entries: {len(hash_database)}\nTotal Time: {time.time() - start_time}s.")