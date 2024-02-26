import random
import webbrowser
from pycrawlermodules import JSONreader

# Getter functions
def gethtmlcontent(key, jsonfile):
    for item in jsonfile:
        if key in item:
            return item[key][0]['description']
            break
    else:
        print("Description not found for the given key.")

def gettitle(key, jsonfile):
    for item in jsonfile:
        if key in item:
            return item[key][0]['title']
            break
    else:
        print("Title not found for the given key.")

# Initialize collected hash database & json_object
json_tuple = JSONreader('jobresult.json')
json_object, hash_database = json_tuple[0], json_tuple[1]
# Pick a random key from existing keys
key = hash_database[random.randint(0,len(hash_database)-1)]
print(f"Selected key: {key}")
# Get relevant info
title, content = gettitle(key, json_object), gethtmlcontent(key, json_object)
# Build HTML string
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <div id="description">
        {content}
    </div>
</body>
</html>
"""
# Write into HTML file
with open('preview.html', 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)
# Open file
webbrowser.open('preview.html', autoraise=False)
print(f"Link to page: https://www.jobup.ch/fr/emplois/detail/{key}/")