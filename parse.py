#!/usr/bin/env python3
import json
import datetime
from functools import lru_cache
import requests
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
import hashlib
from multiprocessing.dummy import Pool as ThreadPool
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
pool = ThreadPool(4)


def parse_full_date(row):
    date = datetime.datetime.strptime(row["BreachDate"], "%Y-%m-%d")
    return date


@lru_cache()
def download_file(url,filename=None):
    if not filename:
        md5=hashlib.md5()
        md5.update(url.encode())
        filename='paste_'+md5.hexdigest()
    try:
        r = requests.get(url, allow_redirects=True, verify=False, timeout=5)
        if r.status_code==200:
            with open(filename, 'wb') as download_filename:
                download_filename.write(r.content)
            print("{} : Paste writen to File".format(md5.hexdigest()))
        else:
            print("{} : File not found".format(url))
    except:
        print("{} : could not download".format(url))



@lru_cache()
def pastebin_download(id):
    base_url_meta="https://scrape.pastebin.com/api_scrape_item_meta.php"
    base_url_item="https://scrape.pastebin.com/api_scrape_item.php"
    params={ "i" : id }
    try:
        # r = requests.get(url, allow_redirects=True, verify=False, timeout=5)
        r = requests.get(base_url_meta, params=params, allow_redirects=False, verify=False, timeout=5)
        if "Error, we cannot find this paste" in r.text:
            print("{} : Paste no longer available".format(id))
        else:
            r = requests.get(base_url_item, params=params, allow_redirects=False, verify=False, timeout=5)
            with open('paste_'+id, 'wb') as download_filename:
                download_filename.write(r.content)
            print("{} : Paste writen to File".format(id))
    except JSONDecodeError:
        print("no json response")
    except Exception as e:
        print(type(e))


json_file=open("json.json",'r')
data=json.load(json_file)
breaches=data["BreachSearchResults"]
pastes=data["PasteSearchResults"]

wd=json_normalize(data=breaches, record_path='Breaches', meta=['Alias','DomainName'] )
wd["BreachDate"] = wd.apply(parse_full_date, axis=1)

for user in pastes:
    for paste in user["Pastes"]:
        # print("{}:{} = {}".format(paste["Source"],paste["Id"],paste["Title"]))
        if paste["Source"] == "Pastebin":
            pass
            # pastebin_download(paste["Id"])
        elif paste["Source"] == "AdHocUrl":
            download_file(paste["Id"])
        else:
            print(paste["Source"])

# results = pool.map(my_function, my_array)

# plt.hist(wd["BreachDate"])
# plt.show()

# plt.hist(wd["Name"])
# plt.xticks(rotation="vertical")
# plt.show()
