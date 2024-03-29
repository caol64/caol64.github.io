import xml.etree.ElementTree as ET
import requests


HOST = 'babyno.top'
KEY = '898460573df54f0a8b6eb4bb09469c18'


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


def ping_bing(url_list):
    # Prepare the URL and headers.
    url = f"https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey={KEY}"
    headers = {
      'Content-Type': 'application/json; charset=utf-8',
    }

    # Prepare the body data.
    data = {
      "siteUrl": HOST,
      "urlList": url_list
    }

    # Send the POST request.
    response = requests.post(url, headers=headers, json=data)
    return response


if __name__ == "__main__":

    sitemap_path = "../sitemap.xml"
    url_list = get_latest_posts(sitemap_path, 9)
    url_list.insert(0, f'https://{HOST}/')
    print(url_list)

    response = ping_bing(url_list)
    # Print the response.
    print(response.status_code)
    print(response.text)
    print("Data: ", response.request.body)
