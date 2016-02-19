#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import remove
from grab import Grab
from json import loads
from urllib.parse import quote
from urllib.request import urlopen

input_data = 'data.txt'
output_data = 'data.txt'
page = int(26)
pages = int(21)

def data_get(pages, data_in_page, file):

    url = 'http://www.albumoftheyear.org/ratings/1-pitchfork-highest-rated/all/'
    data = open(file, 'w')
    data_dict = {}
    data_list = []

    try:
        for i in range(pages):
            site_url = (url + str(i))
            name = ('temp_page' + str(i) + '.html')
            site = Grab(log_file= name)
            site.go(site_url)

            if i > 0:
                for k in range(data_in_page):
                    if k > 0:

                        divid = '//div[@id="post-' + str(k) + '"]'
                        number = str(site.xpath_number(divid + '//*[@class="listLargeTitle"]'))
                        albumartist = site.xpath_text(divid + '//a')

                        for i in range(len(albumartist)):
                            if albumartist[i] == '-':
                                stoping = i
                                break

                        artist = albumartist[:stoping-1]
                        album = albumartist[stoping+2:]
                        reliase_temp = str(site.xpath_text(divid + '//*[@style="margin-bottom:2px; color: #444;"]'))
                        reliase = reliase_temp[len(reliase_temp)-4:]

                        if str(site.xpath_text(divid + '//div[@style="float:left;"]//a')) != 'Source':
                            genre = str(site.xpath_text(divid + '//div[@style="float:left;"]//a'))
                        else: genre = 'none'

                        ratings = str(site.xpath_text(divid + '//*[@class="listScoreValue"]'))
                        data.write(number + '|' + artist + '|' + album + '|' + reliase + '|'
                                   + genre + '|' + ratings + '|' + ' \n')
                        data_dict = {'num' : number, 'art': artist, 'alb': album, 'yea': reliase, 'rat': ratings}
                        data_list.append(data_dict)

        data.close()
        data_dict.clear()
        data_list.clear()

        for i in range(pages):
            name = ('temp_page' + str(i) + '.html')
            remove(name)

        for i in range(len(data_list)):
            print(data_list[i])

        return data_list

    except:

        try:
            print('Error...')
            for i in range(pages):
                name = ('temp_page' + str(i) + '.html')
                remove(name)

        except: print('Error...')

def data_read(file):

    data_list = []
    data_final = []
    data = open(file, 'r')

    for line in data:
        text = line.split('|')
        data_temp = text
        data_list.append(data_temp)

    for i in range(len(data_list)):
        data_dict = dict(position=data_list[i][0], artist=data_list[i][1], albums=data_list[i][2], year=data_list[i][3],
                     genre=data_list[i][4], rating=data_list[i][5])

        data_final.append(data_dict)

    return data_final

def data_info(data_final):

    nogenre = 0
    percent = 0

    try:
        for i in range(len(data_final)):
            if data_final[i]['genre'] != 0:
                disk_url = 'https://api.discogs.com/database/search?'
                #disk_find_artist = 'artist=' + data_final[i]['artist']
                disk_find_albums = 'release_title=' + data_final[i]['albums']
                disk_find_year = 'year=' + data_final[i]['year']
                #disk_find_url = disk_find_albums + '&' + disk_find_artist + '&' + disk_find_year +
                disk_find_url = disk_find_albums + '&' + disk_find_year + '&per_page=1&page=1&token=xSHfcMkUYLPrlhfapEaMVLyubAqWQLQJQjaBaoSD'
                find = disk_url + quote(disk_find_url, safe='&/?=')
                disk_data = urlopen(find).read()
                disk_json = loads(disk_data.decode('utf-8'))
                percent = percent + 1
                prog = int(percent) / int(len(data_final)) * 100
                try:

                    genre = str(disk_json['results'][0]['genre'])
                    style = str(disk_json['results'][0]['style'])
                    print('Progress: ', round(prog, 2), '% ', data_final[i]['position'], ' ', data_final[i]['artist'], '-', data_final[i]['albums'], genre, style)
                    genrefile = open('genre.txt', 'a')
                    genrefile.write(
                        data_final[i]['position'] + '|' + data_final[i]['artist'] + '|' + data_final[i]['albums'] + '|' +
                        data_final[i]['year'] + '|' + genre + '|' + style + '|' + data_final[i]['rating'] + '\n')
                    genrefile.close()
                except:
                    nogenre = nogenre + 1
                    print('Progress: ', round(prog, 2), '% ', data_final[i]['position'], ' ', data_final[i]['artist'], '-', data_final[i]['albums'], 'genreERROR')
                    genrefile = open('genre.txt', 'a')
                    genrefile.write(
                        data_final[i]['position'] + '|' + data_final[i]['artist'] + '|' + data_final[i]['albums'] + '|' +
                        data_final[i]['year'] + '|' + 'genreERROR' + '|' + 'styleERROR' + data_final[i]['rating'] + '\n')
                    genrefile.close()
                    disk_json_str = str(disk_json)
                    error_url = open('errorURL.txt', 'a')
                    error_url.write(find + '\n' + disk_json_str + '\n')
                    error_url.close()
                    continue

        print('\n Bad genres:' , nogenre)
    except KeyboardInterrupt: print('\n Bad genres:' , nogenre, '\n', 'Program has been stopped...')


    return 0

data_get(pages, page, output_data)
data_info(data_read(input_data))
