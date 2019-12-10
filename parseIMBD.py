import requests
from bs4 import BeautifulSoup as BS

def prettify_page(url):
    page = requests.get(url)
    soup = BS(page.content, 'html.parser').html
    return soup

​page_1 = prettify_page("https://www.imdb.com/search/title/?title_type=feature&release_date=2017-01-01,2019-12-31&countries=us&sort=boxoffice_gross_us,desc&count=250&ref_=adv_prv")
​
page_2 = prettify_page('https://www.imdb.com/search/title/?title_type=feature&release_date=2017-01-01,2019-12-31&countries=us&sort=boxoffice_gross_us,desc&count=250&start=251&ref_=adv_nxt')

def parse_movies(soup):
    movies_titles = []
    items = soup.find_all('div', class_='lister-item')
    n = len(list(items))
    for item in items:
        found = soup.find('a')
                          #href = lambda x: x and x.endswith('adv_li_tt'))
        movies_titles.append(found)
        print(found)
    #print(movies_titles)

