# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 08 10 13:09
# ====================================================================================

import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import csv
import threading

def getCountryLinks():
    url = 'https://www.industryabout.com/country-territories-3'
    res = requests.get(url)
    soup = BeautifulSoup(res.content.decode())
    div = soup.find('div', attrs={'class': 'category-list'})
    countryLinks = []
    for a in div.find_all('a'):
        countryLinks.append(a['href'])
    return countryLinks


def getCountryIndustryLinks(countryLink):
    url = 'https://www.industryabout.com' + countryLink
    res = requests.get(url)
    soup = BeautifulSoup(res.content.decode())
    div = soup.find('div', attrs={'class': 'cat-children'})
    countryCategoryLinks = []
    for a in div.find_all('a'):
        countryCategoryLinks.append(a['href'])
    countryIndustryLinks = []
    for countryCategoryLink in tqdm(countryCategoryLinks):
        while True:
            try:
                url = 'https://www.industryabout.com' + countryCategoryLink
                res = requests.get(url)
                soup = BeautifulSoup(res.content.decode())
                for a in soup.table.find_all('a'):
                    if (a['href'] == '#') or (a['href'] in countryLinks):
                        continue
                    countryIndustryLinks.append(a['href'])
                break
            except:
                time.sleep(20)

    time.sleep(5)
    return countryIndustryLinks


def getIndustryDetail(industryLink):
    while True:
        try:
            url = 'https://www.industryabout.com' + industryLink
            res = requests.get(url)
            soup = BeautifulSoup(res.content.decode())
            name = soup.find('h2', itemprop='name').text.strip()
            country = soup.find('dd', attrs={'class', 'parent-category-name'}).find('a').text
            category = soup.find('dd', attrs={'class', 'category-name'}).find('a').text
            body = []
            for s in soup.find('div', itemprop='articleBody').find_all('strong'):
                body.append(s.text)
                if 'Coordinates' in s.text:
                    coord = s.text.split(' ')[1].split(',')
            data = [name, country, category, coord, body]
            with open("all.csv", 'a', newline='', encoding='utf-8') as t:
                writer = csv.writer(t)
                writer.writerow(data)
            break
        except:
            time.sleep(20)


# countryLinks = getCountryLinks()
# pd.DataFrame(countryLinks).to_csv('countryList.csv', index=False, header=False)
# countryLinks = pd.read_csv('countryList.csv', header=None)
# flag = 0
# for countryLink in tqdm(countryLinks[0]):
#     countryIndustryLinks = getCountryIndustryLinks(countryLink)
#     if flag:
#         pd.DataFrame(countryIndustryLinks).to_csv('countryIndustryLinks.csv', index=False, header=False)
#         flag = 0
#     else:
#         pd.DataFrame(countryIndustryLinks).to_csv('countryIndustryLinks.csv', mode='a', index=False, header=False)
industryLinks = pd.read_csv('countryIndustryLinks.csv', header=None)
# for industryLink in tqdm(industryLinks[0]):
#     getIndustryDetail(industryLink)

threads = [threading.Thread(target=getIndustryDetail, args=(idx,)) for idx in industryLinks[0]]

for thread in threads:
    thread.start()
    while True:
        if len(threading.enumerate()) <= 200:
            break
