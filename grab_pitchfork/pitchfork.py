import time
from json import loads
from grab import Grab, error
from urllib.parse import quote
from bs4 import BeautifulSoup as Soup
from urllib.request import urlopen, HTTPError
from multiprocessing.dummy import Pool as ThreadPool

'''govnocode'''
class pitchfork:

    pitc_url = 'http://pitchfork.com/best/high-scoring-albums/'
    disc_url = 'https://api.discogs.com/database/search?'

    grab_header = '//div[@id="main"]//*[@class="object-header"]'
    grab_artist = '//div[@class="info"]/h1'
    grab_album  = '//div[@class="info"]/h2'
    grab_year_1 = '//div[@class="info"]/h3'
    grab_year_2 = '//div[@class="info"]/h4'
    grab_rating = '//div[@class="info"]/span'

    def __init__(self, discogs_api_token):

        self.token = discogs_api_token
        self.test = None
        try:
            test = Grab()
            test.go(self.pitc_url)
            if test.doc.select(self.grab_header).text() == '8.0+ Reviews':
                self.test = True
            urlopen(self.disc_url + '&per_page=1&token=' + self.token)
        except IndexError:
            print('Pitchfork...')
            self.test = False
        except HTTPError:
            print('Discogs')
            self.test = False

        if self.test is True:
            self.getFile(header=['Artist', 'Album', 'Genre', 'Style', 'Year', 'Ratings'])
            self.__start__()
        else:
            print('test is', self.test)
            exit(1)

    def __start__(self):

        page = 1
        page_not_found = None
        while page_not_found == None:

            try:
                print('Page', page)

                pitchfork_page = Grab()
                pitchfork_page.go(self.pitc_url + str(page))
                soup = Soup(pitchfork_page.doc.select('//div[@id="main"]/ul[@class="object-grid "]').html(), 'lxml')
                albums_on_page = []

                for link in soup.find_all('a', href=True):
                    albums_on_page.append('http://pitchfork.com' + link['href'])
                    
                #TODO FAIL http://stackoverflow.com/questions/19846332/python-threading-inside-a-class
                try:
                    pool = ThreadPool(1)
                    pool.map(self.getAlbum, albums_on_page)
                except RuntimeError:
                    time.sleep(60)
                    pool = ThreadPool(int(len(albums_on_page) / 2))
                    pool.map(self.getAlbum, albums_on_page)

                page += 1

                #if page > 1:
                #   page_not_found = True

            except IndexError as e:
                print(e)
                page_not_found = True

    def getAlbum(self, link):

        album_page = Grab()
        album_page.go(link)
        self.artist = album_page.doc.select(self.grab_artist).text()
        self.album = album_page.doc.select(self.grab_album).text()
        try:
            self.year = int(album_page.doc.select(self.grab_year_1).text()[-4:])
        except:
            self.year = int(album_page.doc.select(self.grab_year_2).text()[-4:])
        self.rating = album_page.doc.select(self.grab_rating).text()
        self.genre = 'None'
        self.style = 'None'
        self.Discogs()

    def DiscogsRateLimit(self, error):
        '''Requests are throttled by the server to 240 per minute per IP address'''
        try:
            print('Wait 60 seconds, because:', error)
            time.sleep(60)
            print('Connect to api.discogs.com...')
            self.disc_data = urlopen(self.disc_query).read()
        except HTTPError as e:
            self.DiscogsRateLimit(e)

    def DiscogsQuery(self, artist=None, album=None, year=None):
        ''''''
        try:
            self.disc_query = self.disc_url

            if artist != None:
                self.disc_query += '&artist=' + artist
            if album != None:
                self.disc_query += '&release_title=' + album
            if year != None:
                self.disc_query += '&year=' + str(year)

            self.disc_query += '&per_page=1&page=1&token=' + self.token
            self.disc_query = quote(self.disc_query, safe=':&/?=')
        except:
            self.disc_query = None
        try:
            self.disc_data = urlopen(self.disc_query).read()
            self.disk_resp = loads(self.disc_data.decode('utf-8'))
        except HTTPError as e:
            self.DiscogsRateLimit(e)

    def Discogs(self):
        ''''''
        # TODO Recursion!
        self.DiscogsQuery(artist=self.artist, album=self.album, year=self.year)
        try:
            self.genre = self.disk_resp['results'][0]['genre'][0]
            if len(self.disk_resp['results'][0]['style']) > 0:
                self.style = self.disk_resp['results'][0]['style'][0]
            else:
                self.style = 'None'
        except IndexError:
            # try without &release_name=
            self.DiscogsQuery(artist=self.artist, year=self.year)
            try:
                self.genre = self.disk_resp['results'][0]['genre'][0]
                if len(self.disk_resp['results'][0]['style']) > 0:
                    self.style = self.disk_resp['results'][0]['style'][0]
                else:
                    self.style = 'None'
            except IndexError:
                # try without &year=
                self.DiscogsQuery(artist=self.artist, album=self.album)
                try:
                    self.genre = self.disk_resp['results'][0]['genre'][0]
                    if len(self.disk_resp['results'][0]['style']) > 0:
                        self.style = self.disk_resp['results'][0]['style'][0]
                    else:
                        self.style = 'None'
                except IndexError:
                    # try without &artist=
                    self.DiscogsQuery(album=self.album, year=self.year)
                    try:
                        self.genre = self.disk_resp['results'][0]['genre'][0]
                        if len(self.disk_resp['results'][0]['style']) > 0:
                            self.style = self.disk_resp['results'][0]['style'][0]
                        else:
                            self.style = 'None'
                    except IndexError:
                        self.style = 'None'
                        self.style = 'None'

        self.getFile()

    def getFile(self, filename='data', header=None, format='csv'):
        ''''''
        name = filename + '.' + format

        if format == 'csv':
            import csv
            with open(name, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                if header != None:
                    writer.writerow(header)
                else:
                    writer.writerow([self.artist, self.album, self.genre, self.style, self.year, self.rating])


if __name__ == '__main__':
    time_start = time.time()
    DISCOGS = 'xSHfcMkUYLPrlhfapEaMVLyubAqWQLQJQjaBaoSD'

    go = pitchfork(DISCOGS)

    data_end = float(format(time.time() - time_start))
    print('Process finished at ', round(data_end, 6))
