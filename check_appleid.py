# -*- coding: utf-8 -*-
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


password = 'qwerty'


def generate_mail_list(mail):
    """Создаем и возвращаем возможные варианты опечаток для mail"""
    # for elem in mail:
    #    pass

    maillist = ('petrusha12@mail.ru', 'petrusha23@mail.ru', 'pet4@gmail.com')
    return maillist


def check_mail_list(maillist, password):
    """Проверяем список"""
    browser = webdriver.Firefox()
    browser.set_window_position(0, 0)
    browser.set_window_size(900, 600)
    browser.get('https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/'
                'ra/ng/pp/1058480145/testflight/external')
    sleep(5)
    browser.switch_to.frame(browser.find_element_by_id("authFrame"))

    for mail in maillist:
        try:
            print('Try email:', mail)
            mail_form = browser.find_element_by_id('appleId')
            mail_form.send_keys(mail)
            pass_form = browser.find_element_by_id('pwd')
            pass_form.send_keys(password + Keys.RETURN)
            sleep(5)  # 3 2 1
            mail_form.clear()  # exception if auth = true
        except:
            print('My e-mail:', mail)
            break

    browser.close()

if __name__ == '__main__':
    check_mail_list(maillist=generate_mail_list(mail='test@my.ru'),
                    password=password)
