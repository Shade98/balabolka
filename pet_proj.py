import telebot as tb 
import requests as rq 
from bs4 import BeautifulSoup as bs
import csv


def bot():
    token = '6712535574:AAHMdfKp8BTd96lU0VtkSYwCLt5Hw6v8aCs'
    bot = tb.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start_message(message:str):
        answer = bot.send_message(message.chat.id,f'Прувейт {message.chat.username}!\nКакой чемпион тебя интересует?')
        bot.register_next_step_handler(answer,find_champ)

    @bot.message_handler(func=lambda answer: answer.text is not None and '/' not in answer.text)
    def find_champ(answer):
        data = csv.reader(open('db.csv','r'),delimiter=',')
        champ = str(answer.text).lower()
        i = 165
        for row in data:            
            if row[0] != 'name':
                if champ == row[0].lower() :                    
                    bot.send_message(answer.chat.id,f'{row[0]}\n{row[1]}\n{row[3]}\n{row[2]}')                    
                    break
                elif i != 0:
                    i-=1
                    continue
                else:
                    bot.send_message(answer.chat.id,'Такого чемпиона не существует,либо была допущена ошибка в написании имени')
            else:
                continue


    bot.polling()

def scraper():
    def get_html(url):
        response = rq.get(url)
        return response.text
    def get_data(html):
        soup = bs(html,'lxml')
        champions = soup.find('div',class_='style__List-sc-13btjky-2 IorQY')
        for champ in champions:
            name = champ.find('span',class_='style__Text-sc-n3ovyt-3 kThhiV').text
            img = champ.find('span',class_='style__ImageContainer-sc-n3ovyt-1 jxXGFs').find('img').get('src')
            bio_url = champ.get('href')
            bio_url = 'https://www.leagueoflegends.com/'+bio_url
            role = get_role_n_bio(bio_url)[0]
            bio = get_role_n_bio(bio_url)[1]
            data = {
                 'name':name,
                 'role':role,
                 'img':img,
                 'bio':bio
            }
            to_csv(data)
    def to_csv(data):
        with open("db.csv",'a') as file:
            writer = csv.writer(file)
            writer.writerow([data['name'],data['role'],data['img'],data['bio']])
    def get_role_n_bio(url):
        html = get_html(url)
        soup = bs(html,'lxml')
        role = soup.find('div',class_='style__Specs-sc-8gkpub-8 guWCTG').find('ul').find('li',class_='style__SpecsItem-sc-8gkpub-12 EGSZS').find('div',class_='style__SpecsItemValue-sc-8gkpub-15 fTPDyp').text
        bio = soup.find('p').text
        return role,bio
    
    with open('db.csv','w') as file:
        writer = csv.writer(file)
        writer.writerow(['name','role','img','bio'])

    url = 'https://www.leagueoflegends.com/ru-ru/champions/'
    html = get_html(url)
    get_data(html)
    
# scraper()
bot()
