from grab import Grab
from json import loads
from urllib.parse import quote
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup


class pitchfork:

    pitchfork_url = 'http://pitchfork.com/best/high-scoring-albums/'
    disc_url = 'https://api.discogs.com/database/search?'

    def __init__(self, discogs_api_token):

        self.token = discogs_api_token
        self.__test = None

        try:

            test = Grab()
            test.go(self.pitchfork_url)

            if test.doc.select('//div[@id="main"]//*[@class="object-header"]').text() == '8.0+ Reviews':
                self.__test = True

            test = urlopen(self.disc_url + '&per_page=1&token=' + self.token)


        except IndexError:
            print('Pitchfork...')
            self.__test = False

        except HTTPError:
            print('Discogs...')
            self.__test = False

        if self.__test is True:
            header = ['Artist', 'Album', 'Year', ['Genre', 'None'], ['Style', 'None'], 'Ratings', 'API link']
            self.oupput(header)
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
                soup = BeautifulSoup(pitchfork_page.doc.select('//div[@id="main"]/ul[@class="object-grid "]').html(), 'lxml')
                albums_on_page = []

                for link in soup.find_all('a', href=True):
                    albums_on_page.append('http://pitchfork.com' + link['href'])

                for i in range(len(albums_on_page)):
                    self.album(albums_on_page[i])

                page += 1

            except IndexError as e:
                print(e)
                page_not_found = True

    def album(self, link):

        album_page = Grab()
        album_page.go(link)
        artist = album_page.doc.select('//div[@class="info"]/h1').text()
        album = album_page.doc.select('//div[@class="info"]/h2').text()
        year = album_page.doc.select('//div[@class="info"]/h3').text()[-4:]
        ratings = album_page.doc.select('//div[@class="info"]/span').text()
        self.info(artist, album, year, ratings)

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

        file = open('results.txt', 'a')
        file.write(str(array[0]) + ' | ' + str(array[1]) + ' | ' + str(array[2]) + ' | ' + str(array[3][0]) +
                   ' | ' + str(array[4][0]) + ' | ' + str(array[5]) + ' | ' + str(array[6]) + '\n')



if __name__ == '__main__':
    DISCOGS = 'xSHfcMkUYLPrlhfapEaMVLyubAqWQLQJQjaBaoSD'
    go = pitchfork(DISCOGS)

