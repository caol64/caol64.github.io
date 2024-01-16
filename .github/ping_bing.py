import xml.etree.ElementTree as ET
import requests
import json
import os


def get_latest_posts(sitemap_path, n=10):
    # Parse the XML sitemap.
    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    # Namespace dictionary to find the 'loc' and 'lastmod' tags.
    namespaces = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    # Get all URLs.
    urls = [(url.find('s:loc', namespaces).text, url.find('s:lastmod', namespaces).text)
            for url in root.findall('s:url', namespaces)
            if "/posts/2" in url.find('s:loc', namespaces).text]

    # Sort URLs by the lastmod tag (in descending order), hence most recent pages come first.
    urls.sort(key=lambda x: x[1], reverse=True)

    # Return the n most recent URLs.
    return [url[0] for url in urls[:n]]


# Test the function.
sitemap_path = "../sitemap.xml"  # replace the sitemap file path accordingly
url_list = get_latest_posts(sitemap_path, 9)
url_list.insert(0, 'https://babyno.top/')
print(url_list)

# Prepare the URL and headers.
url = 'https://www.bing.com/indexnow'
headers = {
  'Content-Type': 'application/json; charset=utf-8',
}

API_KEY = os.getenv("BING_API_KEY")

# Prepare the body data.
data = {
  "host": "babyno.top",
  "key": API_KEY,
  "keyLocation": f"https://babyno.top/${API_KEY}.txt",
  "urlList": url_list
}

# Send the POST request.
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print the response.
print(response.text)
