import time
import os
from grab import Grab
from json import loads
from urllib.parse import quote
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup as Soup
from multiprocessing.dummy import Pool as ThreadPool

#govnocode

class pitchfork:
    ''''''
    pitchfork_url = 'http://pitchfork.com/best/high-scoring-albums/'
    disc_url = 'https://api.discogs.com/database/search?'

    def __init__(self, discogs_api_token):

        self.time_start = time.time()
        self.token = discogs_api_token
        self.test = None

        try:
            test = Grab()
            test.go(self.pitchfork_url)
            if test.doc.select('//div[@id="main"]//*[@class="object-header"]').text() == '8.0+ Reviews':
                self.__test = True
            test = urlopen(self.disc_url + '&per_page=1&token=' + self.token)
        except IndexError:
            print('Pitchfork...')
            self.test = False
        except HTTPError:
            print('Discogs...')
            self.test = False

        if self.test is True:
            self.oupput(array=['Artist', 'Album', 'Year', ['Genre', 'None'], ['Style', 'None'], 'Ratings', 'API link'])
            self.get()
        else:
            print('test is', self.__test)
            exit(1)

    def get(self):

        page = 1
        page_not_found = None
        while page_not_found == None:
            try:
                print('Page', page)
                pitchfork_page = Grab()
                pitchfork_page.go(self.pitchfork_url + str(page))
                soup = Soup(pitchfork_page.doc.select('//div[@id="main"]/ul[@class="object-grid "]').html(), 'lxml')
                albums_on_page = []
                for link in soup.find_all('a', href=True):
                    albums_on_page.append('http://pitchfork.com' + link['href'])
                try:
                    pool = ThreadPool(int(len(albums_on_page) / 2))
                    pool.map(self.album, albums_on_page)
                except RuntimeError:
                    time.sleep(60)
                    pool = ThreadPool(int(len(albums_on_page) / 2))
                    pool.map(self.album, albums_on_page)
                page += 1

                #if page > 2:
                #    page_not_found = True

            except IndexError as e:
                print(e)
                page_not_found = True

    def album(self, link='None'):

        album_page = Grab()
        album_page.go(link)
        artist = album_page.doc.select('//div[@class="info"]/h1').text()
        album = album_page.doc.select('//div[@class="info"]/h2').text()
        try:
            year = int(album_page.doc.select('//div[@class="info"]/h3').text()[-4:])
        except:
            year = int(album_page.doc.select('//div[@class="info"]/h4').text()[-4:])
        ratings = album_page.doc.select('//div[@class="info"]/span').text()
        #dict = {'Artist': artist, 'Album': album, 'Year': str(year), 'Ratings' : str(ratings).replace('.', ',')}
        self.info(artist, album, year, ratings)

    def DiscogsQuery(self, artist=None, album=None, year=None):

        try:
            self.discogs_query = self.disc_url

            if artist != None:
                self.discogs_query += '&artist=' + artist
            if album != None:
                self.discogs_query += '&release_title=' + album
            if year != None:
                self.discogs_query += '&year=' + str(year)

            self.discogs_query += '&per_page=1&page=1&token=' + self.token
            self.discogs_query = quote(self.discogs_query, safe=':&/?=')

        except:
            self.discogs_query = None

    def DiscogsRateLimit(self, error):
        '''Requests are throttled by the server to 240 per minute per IP address'''
        try:
            print('Wait 60 seconds, because:', error)
            time.sleep(60)
            print('Connect to api.discogs.com...')
            self.info_data = urlopen(self.discogs_query).read()

        except HTTPError as e:
            self.DiscogsRateLimit(e)

    def info(self, artist, album, year, ratings):

        array = []
        disk_find_albums = 'release_title=' + album
        disk_find_year = 'year=' + year
        disk_find_url = disk_find_albums + '&' + disk_find_year + \
                        '&per_page=1&page=1&token=' + self.token
        api = self.disc_url + quote(disk_find_url, safe='&/?=')
        array.append(artist)
        array.append(album)
        array.append(year)
        null_array = ['None', 'None']

        try:
            info_data = urlopen(self.disc_url + quote(disk_find_url, safe='&/?=')).read()
            info_json = loads(info_data.decode('utf-8'))
            genre = info_json['results'][0]['genre']
            style = info_json['results'][0]['style']

            if len(genre) > 0:
                array.append(genre)
            else:
                raise Exception
            if len(style) > 0:
                array.append(style)
            else:
                array.append(null_array)
            array.append(ratings)
            array.append('None')
        except:
            array.append(null_array)
            array.append(null_array)
            array.append(ratings)
            array.append(api)

        self.oupput(array)

    def oupput(self, array):

        file = open('results.csv', 'a')
        file.write(str(array[0]) + ';' + str(array[1]) + ';' + str(array[2]) + ';' + str(array[3][0]) +
                   ';' + str(array[4][0]) + ';' + str(array[5]) + ';' + str(array[6]) + '\n')
        data_end = float(format(time.time() - self.time_start))
        data_end = round(data_end, 10)
        #file.write(str(array[0]) + ';' + str(data_end) + ';' + str(self.pool_thread) + '\n')
        self.time_start = time.time()
        file.close()



if __name__ == '__main__':
    time_start = time.time()
    DISCOGS = 'xSHfcMkUYLPrlhfapEaMVLyubAqWQLQJQjaBaoSD'

    go = pitchfork(DISCOGS)

    data_end = float(format(time.time() - time_start))
    print('Process finished at ', round(data_end, 6))

