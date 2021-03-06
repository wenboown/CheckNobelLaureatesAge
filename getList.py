"""
Bo Wen
2018
This code grabs the info from Nobelprize.org

I borrowed some code from https://github.com/datasets/s-and-p-500-companies/blob/master/scripts/constituents.py
Thanks to the authors.
"""

from bs4 import BeautifulSoup
import csv
from os import mkdir
from os.path import exists, join
import urllib.request as request
import time
import re

if not exists('tmp'):
    mkdir('tmp')

base_url = "https://www.nobelprize.org"
d = {
    'physics': {},
    'chemistry': {},
    'medicine': {},
    'literature': {},
    'economic-sciences': {},
}
for k, v in d.items():
    v['url'] = '/nobel_prizes/'+k+'/laureates/'


def tmp(filename):
    return join('tmp', filename)


def extract(cache):
    source_page = open(cache).read()
    return BeautifulSoup(source_page, 'html.parser')


def retrieve(url, cache):
    if not exists(cache):
        request.urlretrieve(url, cache)
        time.sleep(1)  # slow down the download, don't give pressure to nobelprize.org server


def list_by_year():
    for k, v in d.items():
        cache = tmp(k+'_list.html')
        retrieve(base_url+v['url'], cache)
        source_page = open(cache).read()
        v['soup'] = BeautifulSoup(source_page, 'html.parser')
        temp_list = v['soup'].find_all('div', class_="by_year")

        with open(k+'.csv', 'w', newline='') as csv_file:
            fieldnames = ['award_year', 'name', 'birth_date', 'birth_year', 'work', 'work_year', 'work_age', 'award_age', 'number_of_years_in_work']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for i in temp_list:
                if i.h6 is None:  # when this year's prize hasn't been announced yet, or not awarded
                    pass
                else:
                    award_year = int(i.h3.a.contents[0][-4:])
                    a_list = i.h6.find_all('a')
                    for aa in a_list:
                        name = aa.contents[0]
                        link = aa['href'].split('/')
                        a_cache = tmp(link[-2]+'_'+link[-1])
                        retrieve(base_url+aa['href'], a_cache)
                        a_source = open(a_cache).read()
                        a_soup = BeautifulSoup(a_source, 'html.parser')
                        birth_date = a_soup.find('span', attrs={'itemprop': 'birthDate'}).contents[0]
                        birth_year = int(re.search(r"([1-3][0-9]{3})", birth_date).group(1))
                        award_age = award_year - birth_year
                        work_h2 = a_soup.find('h2', string='Work')
                        if work_h2 is not None:
                            work = work_h2.find_next_sibling().contents[0]
                            try:
                                list_of_years = re.findall(r"([1-3][0-9]{3})", work)
                                work_year = max(list(map(int, list_of_years)))
                                work_age = work_year - birth_year
                            except (AttributeError, ValueError):
                                list_of_years = []
                                work_year = 0
                                work_age = 0
                        else:
                            work = ''
                            list_of_years = []
                            work_year = 0
                            work_age = 0
                        writer.writerow({'award_year': award_year,
                                         'name': name,
                                         'birth_date': birth_date,
                                         'birth_year': birth_year,
                                         'work': work,
                                         'work_year': work_year,
                                         'work_age': work_age,
                                         'award_age': award_age,
                                         'number_of_years_in_work': len(list_of_years)})

                        print('{} {}'.format(award_year, name))


if __name__ == '__main__':
    list_by_year()

