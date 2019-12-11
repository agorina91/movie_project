import requests
import time
from bs4 import BeautifulSoup as BS
import urllib
from urllib.parse import quote

import config

if config.pycharm:
    import pymysql
    cnx = pymysql.connect(
        host=config.host,
        user=config.user,
        passwd=config.pw,
        database='movie_db'
    )
else:
    import mysql.connector
    cnx = mysql.connector.connect(
        host=config.host,
        user=config.user,
        passwd=config.pw,
        database='movie_db'
    )

cursor = cnx.cursor()


def prettify_page(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    page = requests.get(url, headers=headers, timeout=5)
    soup = BS(page.content, 'html.parser').html
    return soup


page_1 = prettify_page(
    'https://www.imdb.com/search/title/?title_type=feature&release_date=2017-01-01,2019-12-31&countries=us&sort=boxoffice_gross_us,desc&count=250&ref_=adv_prv')

page_2 = prettify_page(
    'https://www.imdb.com/search/title/?title_type=feature&release_date=2017-01-01,2019-12-31&countries=us&sort=boxoffice_gross_us,desc&count=250&start=251&ref_=adv_nxt')


def parse_movies(soup):
    movies_dict = {}
    items = soup.find_all('div', class_='lister-item')

    for item in items:

        movie_id = item.find('h3', class_='lister-item-header')
        movie_id = movie_id.find('a')
        movie_id = movie_id['href']

        movie_id = movie_id.replace('/title/', '')
        movie_id = movie_id.replace('/', '')
        movie_id = movie_id.replace('?ref_=adv_li_tt', "")

        title = item.find('h3', class_='lister-item-header')
        title = title.find('a').string

        user_rating = item.find('div', class_='ratings-imdb-rating')
        if user_rating:
            user_rating = user_rating.find('strong').string
        else:
            user_rating = -1

        user_rating = int(float(user_rating) * 10)

        metascore = item.find('div', class_='ratings-metascore')
        if metascore:
            metascore = metascore.find('span', class_="metascore").string.strip()
        else:
            metascore = -1

        metascore = int(metascore)

        movies_dict[movie_id] = (title, user_rating, metascore)

    return movies_dict


def close_db():
    cursor.close()
    cnx.close()


def add_to_table(movie_dict):
    for movie_id in movie_dict.keys():
        data_movie = {
            'movie_id': movie_id,
            'title': movie_dict[movie_id][0],
            'user_rating': movie_dict[movie_id][1],
            'metascore': movie_dict[movie_id][2],
        }
        # print(data_movie)

        inserting = """INSERT INTO Master_Table  
         (movie_id, title, user_rating, metascore) 
         VALUES (%(movie_id)s, %(title)s, %(user_rating)s, %(metascore)s);"""

        cursor.execute(inserting, data_movie)
        cnx.commit()


def parse_parent_guide(movie_id):
    categories = {}
    url = "https://www.imdb.com/title/" + movie_id + "/parentalguide?ref_=tt_stry_pg"
    soup = prettify_page(url)

    mpaa_rating = soup.find(id="mpaa-rating")

    if mpaa_rating:
        mpaa_rating = mpaa_rating.find_all("td")[1].string
    else:
        mpaa_rating = "None"

    nudity = soup.find('section', id='advisory-nudity')

    if nudity:
        nudity = nudity.find('span', class_='ipl-status-pill').string
    else:
        nudity = 'No Data'

    violence = soup.find('section', id='advisory-violence')

    if violence:
        violence = violence.find('span', class_='ipl-status-pill').string
    else:
        violence = 'No Data'

    profanity = soup.find('section', id='advisory-profanity')

    if profanity:
        profanity = profanity.find('span', class_='ipl-status-pill').string
    else:
        profanity = "No Data"

    alcohol = soup.find('section', id='advisory-alcohol')

    if alcohol:
        alcohol = alcohol.find('span', class_='ipl-status-pill').string
    else:
        alcohol = "No Data"

    frightening = soup.find('section', id='advisory-frightening')

    if frightening:
        frightening = frightening.find('span', class_='ipl-status-pill').string
    else:
        fightening = "No Data"

    categories[movie_id] = (mpaa_rating, nudity, violence, profanity, alcohol, frightening)

    return categories

    # print(f"nudity: {nudity}, violence: {violence}, profanity: {profanity}, alcohol: {alcohol}, frightening: {frightening}")


def parse_all_categories(movie_dict):
    counter = 0
    categories = {}
    for movie_id in movie_dict.keys():
        categories = parse_parent_guide(movie_id)[movie_id]

        inserting = f"UPDATE Master_Table SET MPAA_rating = '{categories[0]}', nudity = '{categories[1]}', violence = '{categories[2]}', profanity = '{categories[3]}', alcohol = '{categories[4]}', frightening = '{categories[5]}' WHERE movie_id = '{movie_id}'"

        cursor.execute(inserting)
        cnx.commit()

        print(inserting)

        if counter % 20 == 0:
            time.sleep(10)
        else:
            time.sleep(1)
        counter += 1

    return categories


def parse_user_ratings(movie_id):
    url = "https://www.imdb.com/title/" + movie_id + "/ratings"
    soup = prettify_page(url)

    table = soup.find('table')

    if not table:
        return [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

    rows = table.find_all('tr')

    vote_array = []
    for row in rows:
        votes = row.find('div', class_='leftAligned').string
        if votes != 'Votes':
            vote_array.append(votes)

    reverse_votes = vote_array[::-1]
    return reverse_votes

def parse_all_uratings(movie_dict):
    counter = 0

    for movie_id in movie_dict.keys():
        parsed_list = parse_user_ratings(movie_id)

        print(parsed_list[0])

        data_user_rating = {
            'movie_id': movie_id,
            'one': parsed_list[0],
            'two': parsed_list[1],
            'three': parsed_list[2],
            'four': parsed_list[3],
            'five': parsed_list[4],
            'six': parsed_list[5],
            'seven': parsed_list[6],
            'eight': parsed_list[7],
            'nine': parsed_list[8],
            'ten': parsed_list[9],
        }

        print(data_user_rating)

        inserting = """INSERT INTO User_Ratings  
         (movie_id, one, two, three, four, five, six, seven, eight, nine, ten) 
         VALUES (%(movie_id)s, %(one)s, %(two)s, %(three)s, %(four)s, %(five)s, %(six)s, %(seven)s, %(eight)s, %(nine)s, %(ten)s);"""

        cursor.execute(inserting, data_user_rating)
        cnx.commit()
        print(inserting)

        if counter % 20 == 0:
            time.sleep(10)
        else:
            time.sleep(1)
        counter += 1



def main():
    new_dict_1 = parse_movies(page_1)
    new_dict_2 = parse_movies(page_2)
    add_to_table(new_dict_1)
    add_to_table(new_dict_2)
    # #parse_all_categories(new_dict_1)
    # parse_all_categories(new_dict_2)


def parse_metacritic(movie_name):
    categories = {}
    # https://www.metacritic.com/movie/bombshell/critic-reviews

    f = {'movie_name': movie_name}
    # encode_movie_name = urllib.parse.urlencode(f)
    # encode_movie_name = urllib.parse.quote(movie_name)
    encode_movie_name = movie_name.lower()
    encode_movie_name = encode_movie_name.replace(' ', '-')

    url = "https://www.metacritic.com/movie/" + encode_movie_name + "/critic-reviews"
    print(f"Url encoded: {url}")

    soup = prettify_page(url)

    review_dates = soup.find('div', id="main_content")
    # review_dates = soup.find('div',  class_= "pmxa_yqj4")
    # review_dates = soup.find('div', class_="pad_btm1")

    #if review_dates:
        # review_dates = mpaa_rating.find_all("td")[1].string
    #    pass
    #else:
    #    review_dates = "None"

    print(review_dates)
    return

    categories[movie_id] = (mpaa_rating, nudity, violence, profanity, alcohol, frightening)

    return categories

    # print(f"nudity: {nudity}, violence: {violence}, profanity: {profanity}, alcohol: {alcohol}, frightening: {frightening}")



# p = parse_user_ratings("tt1825683")
# print(p)

parse_metacritic("Black Panther")