from mysql.connector import MySQLConnection, Error as SQLError
from urllib.request import urlopen, URLError
from json import loads

CONFIG = 'config.ini'


##############################################

class vk(object):

    __SQLuser = None
    __SQLpass = None
    __SQLbase = None
    __SQLhost = None
    __VKtoken = None
    __VKauser = None
    __VKapi   = None
    __systest = None

    __NAME    = 'first_name'
    __SURNAME = 'last_name'
    __GENDER  = 'sex'
    __DOB     = 'bdate'
    __COUNTRY = 'country'
    __CITY    = 'city'
    __SITE    = 'site'
    __TITLE   = 'title'
    __HTOWN   = 'home_town'
    __PHONE   = 'home_phone'
    __STATUS  = 'occupation'

    ''' https://vk.com/dev/fields '''

    _vk_user_response       = None #{}
    _vk_user_deactivated    = None
    _vk_user_id             = None
    _vk_user_first_name     = None
    _vk_user_last_name      = None
    _vk_user_hidden         = None #Если 1 то всё
    _vk_user_sex            = None
    _vk_user_bdate          = None
    _vk_user_country        = None
    _vk_user_city           = None
    _vk_user_home_town      = None #Родной город
    _vk_user_friends_list   = None #Список ID друзей
    _vk_user_domain         = None
    _vk_user_phone         = None #contacts -> mobile_phone
    _vk_user_site           = None
    _vk_user_universities   = None #list:dict: university_name, faculty_name, chair_name,  graduation (bdate!)
    _vk_user_schools        = None #year_graduated
    _vk_user_occupation     = None #type / name
    _vk_user_career         = None #from-until / company / city_name / position
    _vk_user_relation       = None  #0-7
    _vk_user_personal       = None #dict: political, langs, religion, inspired_by, people_main, life_main, smoking,
    _vk_user_connections    = None
    _vk_user_activities     = None
    _vk_user_interests      = None
    _vk_user_music          = None
    _vk_user_movies         = None
    _vk_user_tv             = None
    _vk_user_books          = None
    _vk_user_games          = None
    _vk_user_about          = None

    __API_GET_USER = 'getuser'
    __API_GET_TEST = 'test'


    def __init__(self, filename='config.ini'):

        from configparser import ConfigParser, Error as CPError
        parser = ConfigParser()
        parser.read(filename)

        try:

            print('--- Checking config file:', filename)
            mysql = dict(parser.items('mysql'))
            api = dict(parser.items('api'))
            self.__SQLuser = mysql['user']
            self.__SQLpass = mysql['password']
            self.__SQLbase = mysql['database']
            self.__SQLhost = mysql['host']
            self.__VKtoken = api['token']
            self.__VKauser = api['id']
            self.__VKapi   = api['api']
            self.sql('test')
            self.api('test')

        except CPError as error:
            print('*** File error:', error)
            self.__systest = False

        except KeyError as error:
            print("*** Can't find", error, 'in', filename)
            self.__systest = False

        while self.__systest == False:
            response = input('--- Bad data in config file. Retry? y/n: ')
            if response == 'y': self.__init__()
            elif response == 'n': exit(1)
            else: response = input('--- Bad data in config file. Retry? y/n: ')

    def user(self, user, *args):
        print('--- Call users.get from API server')
        self._vk_user_id = user
        self.api(self.__API_GET_USER, *[self._vk_user_id])

        if self._vk_user_response != None:

            if 'response' in self._vk_user_response:

                try:
                    if 'deactivated' in self._vk_user_response['response'][0]:
                        print('*** User ID:', self._vk_user_id, 'is deactivated')
                        self._vk_user_deactivated = True
                    else:
                        self.data()
                except IndexError:  print('*** ERROR user ID:', self._vk_user_id)

            elif 'error' in self._vk_user_response:
                print('*** ERROR:', self._vk_user_response['error']['error_msg'], self._vk_user_id)
        else:
            print('error')

    def sql(self, args, **kwargs):

        if args == 'test':

            try:

                print('--- Connect to MySQL server:', self.__SQLhost)
                connect = MySQLConnection(host=self.__SQLhost, database=self.__SQLbase,
                                          user=self.__SQLuser, password=self.__SQLpass)

                if connect.is_connected():
                    print('--- Connected to MySQL database', self.__SQLbase)
                    connect.close()

            except SQLError as e:
                print('***', e)
                self.__systest = False

    def api(self, task, *args):
        if task == self.__API_GET_TEST:

            try:

                test = dict(loads(urlopen('https://api.vk.com/method/friends.getMutual?source_uid=2&target_uid=1'
                                          '&v=5.44&access_token=' + self.__VKtoken).read().decode('utf-8')))

                if 'response' in test.keys():
                    print('--- Access token from vk.com was successfully tested')
                if 'error' in test.keys():
                    print('*** Access token from vk.com was not successfully tested: ', test['error']['error_msg'])
                    self.__systest = False

            except URLError as error:
                print('*** URLError:', error)
                self.__systest = False

        if task == self.__API_GET_USER:
            print('--- Get server response for id' + self._vk_user_id)
            self._vk_user_response = dict(loads(urlopen('https://api.vk.com/method/users.get?user_ids='
                                                        +args[0] + '&fields=hidden,sex,bdate,city,country,'
                                                        'home_town,lists,domain,contacts,site,universities,'
                                                        'schools,occupation,relation,personal,connections,'
                                                        'activities&v=5.44&access_token='
                                                        + self.__VKtoken).read().decode('utf-8')))

    def data(self):
        print('--- Analysing JSON data for id' + self._vk_user_id)
        data = self._vk_user_response['response'][0]
        print(data)
        keys = dict.keys(data)
        print(keys)

        if self.__NAME in keys: self._vk_user_first_name    = data[self.__NAME]
        if self.__SURNAME in keys: self._vk_user_last_name  = data[self.__SURNAME]
        if self.__GENDER in keys:

            if data[self.__GENDER] == 1: self._vk_user_sex = 'Женский'
            elif data[self.__GENDER] == 2: self._vk_user_sex = 'Мужской'
            else: self._vk_user_sex = 'Не указан'

        if self.__DOB in keys: self._vk_user_bdate          = data[self.__DOB]
        if self.__COUNTRY in keys: self._vk_user_country    = data[self.__COUNTRY][self.__TITLE]
        if self.__CITY in keys: self._vk_user_city          = data[self.__CITY][self.__TITLE]
        if self.__SITE in keys: self._vk_user_site          = data[self.__SITE]
        if self.__HTOWN in keys: self._vk_user_home_town    = data[self.__HTOWN]
        if self.__PHONE in keys: self._vk_user_phone        = data[self.__PHONE]
        if self.__STATUS in keys:
            if data[self.__STATUS]['type'] == 'work':
                self._vk_user_occupation  = 'Работает'
            if data[self.__STATUS]['type'] == 'university':
                self._vk_user_occupation  = 'Учится'






    def info(self):
        print('> Пользователь №' + self._vk_user_id)
        print('>',self._vk_user_first_name, self._vk_user_last_name)
        print('> Страна:', self._vk_user_country)
        print('> Город:', self._vk_user_city)
        print('> Дата рождения:', self._vk_user_bdate)
        print('> Пол:', self._vk_user_sex)
        print('> Родной город:', self._vk_user_home_town)
        print('> Телефон:', self._vk_user_phone)
        print('> Социальный статус:', self._vk_user_occupation)
        print('> ВУЗ:', self._vk_user_universities)
##############################################

ALL_FIELDS = 'all'
NAME = 'name'
USER = '252921307'
#USER = '66'
try:

    data = vk()

    #data.user('125545', ALL_FIELDS )
    data.user(USER, NAME)
    data.info()


except KeyboardInterrupt as error:
    print(error)
