import csv
import time
from json import loads
from grab import Grab
from urllib.parse import quote
from bs4 import BeautifulSoup as Soup
from urllib.request import urlopen, HTTPError
from multiprocessing.dummy import Pool as ThreadPool

PITC_URL = 'http://pitchfork.com/best/high-scoring-albums/'
DISC_URL = 'https://api.discogs.com/database/search?'
DISC_TOKEN = 'xSHfcMkUYLPrlhfapEaMVLyubAqWQLQJQjaBaoSD'

grab_header = '//div[@id="main"]//*[@class="object-header"]'
grab_artist = '//div[@class="info"]/h1'
grab_album = '//div[@class="info"]/h2'
grab_year_1 = '//div[@class="info"]/h3'
grab_year_2 = '//div[@class="info"]/h4'
grab_rating = '//div[@class="info"]/span'

THREADS = 8
DISCOGS = 'xSHfcMkUYLPrlhfapEaMVLyubAqWQLQJQjaBaoSD'


def DiscogsRateLimit(error, query):
    # Requests are throttled by the server to 240 per minute per IP address
    try:
        print('Wait 30 seconds, because:', error)
        time.sleep(30)
        print('Connect to api.discogs.com...')
        disc_data = urlopen(query).read()
        return disc_data
    except HTTPError as error:
        DiscogsRateLimit(error, query)


def DiscogsQuery(artist=None, album=None, year=None):

    try:
        disc_query = DISC_URL

        if artist != None:
            disc_query += '&artist=' + artist
        if album != None:
            disc_query += '&release_title=' + album
        if year != None:
            disc_query += '&year=' + str(year)

        disc_query += '&per_page=1&page=1&token=' + DISC_TOKEN
        disc_query = quote(disc_query, safe=':&/?=')
    except:
        disc_query = None
    try:
        disc_data = urlopen(disc_query).read()
        disc_resp = loads(disc_data.decode('utf-8'))
    except HTTPError as e:
        disc_data = DiscogsRateLimit(e, disc_query)
        disc_resp = loads(disc_data.decode('utf-8'))

    return disc_resp


def start():

    CSVFile(header=['Artist', 'Album', 'Genre', 'Style', 'Year', 'Rating'])
    page = 1
    page_not_found = None
    while page_not_found == None:

        try:
            print('Page', page)

            pitchfork_page = Grab()
            pitchfork_page.go(PITC_URL + str(page))
            soup = Soup(pitchfork_page.doc.select('//div[@id="main"]/ul[@class="object-grid "]').html(), 'lxml')
            albums_on_page = []

            for link in soup.find_all('a', href=True):
                albums_on_page.append('http://pitchfork.com' + link['href'])

            pool = ThreadPool(THREADS)

            pool.map(pitchfork, albums_on_page)

            page += 1

            # if page > 1:
            #   page_not_found = True

        except IndexError as error:
            print(error)
            page_not_found = True


def pitchfork(link):
    album_page = Grab()
    album_page.go(link)
    artist = album_page.doc.select(grab_artist).text()

    album = album_page.doc.select(grab_album).text()
    try:
        year = int(album_page.doc.select(grab_year_1).text()[-4:])
    except:
        year = int(album_page.doc.select(grab_year_2).text()[-4:])
    rating = album_page.doc.select(grab_rating).text()

    disc_resp = DiscogsQuery(artist=artist, album=album, year=year)
    try:
        genre = disc_resp['results'][0]['genre'][0]
        if len(disc_resp['results'][0]['style']) > 0:
            style = disc_resp['results'][0]['style'][0]
        else:
            style = 'None'
    except IndexError:
        # try without &release_name=
        disc_resp = DiscogsQuery(artist=artist, year=year)
        try:
            genre = disc_resp['results'][0]['genre'][0]
            if len(disc_resp['results'][0]['style']) > 0:
                style = disc_resp['results'][0]['style'][0]
            else:
                style = 'None'
        except IndexError:
            # try without &year=
            disc_resp = DiscogsQuery(artist=artist, album=album)
            try:
                genre = disc_resp['results'][0]['genre'][0]
                if len(disc_resp['results'][0]['style']) > 0:
                    style = disc_resp['results'][0]['style'][0]
                else:
                    style = 'None'
            except IndexError:
                # try without &artist=
                disc_resp = DiscogsQuery(album=album, year=year)
                try:
                    genre = disc_resp['results'][0]['genre'][0]
                    if len(disc_resp['results'][0]['style']) > 0:
                        style = disc_resp['results'][0]['style'][0]
                    else:
                        style = 'None'
                except IndexError:
                    genre = 'None'
                    style = 'None'

    CSVFile(artist=artist,
            album=album,
            genre=genre,
            style=style,
            year=year,
            rating=rating)


def CSVFile(filename='data2', header=None, artist=None, album=None,
            genre=None, style=None, year=None, rating=None):


    name = filename + '.csv'
    art = str(artist).replace('/', '&')
    alb = str(album).replace('"', '').replace('[', '(').replace(']', ')').replace(';', ':')

    with open(name, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        if header != None:
            writer.writerow(header)
        else:
            writer.writerow([art, alb, genre, style, year, float(rating)])


if __name__ == '__main__':
    time_start = time.time()
    try:
        start()
        data_end = float(format(time.time() - time_start))
        print('Process finished at ', round(data_end, 6))
    except KeyboardInterrupt as e:
        print(e)
        data_end = float(format(time.time() - time_start))
        print('Process finished at ', round(data_end, 6))
