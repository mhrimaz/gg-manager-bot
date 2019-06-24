import logging
import os
import random
import datetime
import time
from language_detector import LanguageDetector
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
from telegram import Message, User, Chat, MessageEntity, Document, ChatMember
from random import randint
import nltk
import pymongo
from datetime import datetime
import urllib.request
import requests
from bs4 import BeautifulSoup

games = ['R6', 'R6', 'R6', 'RL', 'RL', 'RL', 'Apex']
forgiveQuotes = ["The weak can never forgive. Forgiveness is the attribute of the strong.",
                 "One of the keys to happiness is a bad memory.",
                 "Forgiveness is not an occasional act, it is a constant attitude.",
                 "There is no love without forgiveness, and there is no forgiveness without love.",
                 "Mistakes are always forgivable, if one has the courage to admit them."]
stickerCount = {}
englishCount = {}
msgCount = {}
floodStat = {}
users = {}
admins = set()
baseClock_5hour = time.time()
baseClock_2sec = time.time()
baseClock_30min = time.time()
languageDetector = LanguageDetector()
GOD = os.environ.get('GOD')
GROUP_ID = os.environ.get('GROUP_ID')
GIF_SOURCE = os.environ.get('GIF_SOURCE')
GIF_SOURCEX = os.environ.get('GIF_SOURCEX')
GIFS = []
GIFSX = []
STICKER_LIMIT = 5
PHINGLISH_LIMIT = 10
TIME_WINDOW = 5

def getAllGifs(gifSourceURL):
    url = gifSourceURL

    response = requests.request("GET", url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    allGifs = []
    for image in soup.findAll('img'):
        v1 = image.get('src')  # get's "src", else "dfr_src"
                                                    # if both are missing - None
        v2 = image.get('data-src',image.get('dfr-src'))
        
        if v1 is not None:
            if v1.startswith('http') and v1.endswith('gif'):
                allGifs.append(v1)
        if v2 is not None:
                if v2.startswith('http') and v2.endswith('gif'):
                    allGifs.append(v2)
    
    
    return allGifs   

try:
    client = pymongo.MongoClient(
        "mongodb+srv://gg-manager-bot-app:" + os.environ.get("GG_API_KEY") +
        "@cluster0-01zqv.mongodb.net/?retryWrites=true")
    fingMessages = client['gg-manager-bot']['fing-messages']
    GIFS = getAllGifs(GIF_SOURCE)
    GIFSX = getAllGifs(GIF_SOURCEX)
except Exception as ex:
    print("exception of type {} occurred. Args: {}".format(
        type(ex).__name__, ex.args))

def getBanStatus():
    global admins
    global users
    global englishCount
    global msgCount
    global stickerCount
    global floodStat
    result = "Flood: "
    for key, value in floodStat.items():
        if (value == True):
            result+=str(users[key])+"\n"
    result+="\nSticker: "
    for key, value in stickerCount.items():
            result+=str(users[key])+" : "+str(value)+"\n"
    result+="\nPhinglish: "
    for key, value in englishCount.items():
            result+=str(users[key])+" : "+str(value)+"\n"
    return result



def unknown(bot, update):
    global admins
    global users
    global englishCount
    global msgCount
    global stickerCount
    global floodStat
    global GIFS
    global GIFSX

    user = update.effective_user
    userID = user.id
    command = update.effective_message.text
    admins = set([admin.user.id for admin in bot.get_chat_administrators(
        update.effective_message.chat.id)])
    print(userID, " => ", str(admins))
    print("user :", command[command.find('@')+1:])
    if(userID in admins):
        if(command.startswith("/forgive")):
            toForgive = users.setdefault(command[command.find('@')+1:], "")
            stickerCount[toForgive] = stickerCount[toForgive]/2
            englishCount[toForgive] = englishCount[toForgive]/2
            msgCount[toForgive] = msgCount[toForgive]/2
            floodStat[toForgive] = False
            update.effective_message.reply_text(random.choice(forgiveQuotes))
        if(command.startswith("/banstat")):
            update.effective_message.reply_text(getBanStatus())
            GIFS = getAllGifs(GIF_SOURCE)
            GIFSX = getAllGifs(GIF_SOURCEX)
        if(command.startswith("/gif")):
            url = GIFS.pop(random.randrange(len(GIFS)))
            urllib.request.urlretrieve(url, 'GG-'+str(update.effective_message.date)+'.gif')  
            bot.send_document(chat_id=GROUP_ID, document=open('GG-'+str(update.effective_message.date)+'.gif', 'rb'))
        if(command.startswith("/gifx")):
            url = GIFS.pop(random.randrange(len(GIFSX)))
            urllib.request.urlretrieve(url, 'GGX-'+str(update.effective_message.date)+'.gif')  
            bot.send_document(chat_id=GROUP_ID, document=open('GGX-'+str(update.effective_message.date)+'.gif', 'rb'))
    else:
        bot.delete_message(update.effective_message.chat.id,
                           update.effective_message.message_id)


def start(bot, update):
    update.effective_message.reply_text("GG ?")


def randomgame(bot, update):
    update.effective_message.reply_text("GG " + random.choice(games))


def roll(bot, update):
    update.effective_message.reply_text("GG " + str(randint(0, 100)))


def isPhinglish(text):
    if(languageDetector.detect(text) == 'english'):
        return False
    countEnglishLetters = 0
    for c in text:
        if ord(c) < 128 and c.isalpha():
            countEnglishLetters += 1
    return countEnglishLetters/len(text) > 0.5


def processPhoto(bot, update):
    global admins
    global baseClock_5hour
    global englishCount

    user = update.effective_user
    userID = user.id
    if(userID in admins):
        return

    if isPhinglish(update.effective_message.caption):
        englishCount[userID] = englishCount.setdefault(userID, 0) + 1
    else:
        return

    timenow = time.time()
    temp = timenow-baseClock_5hour
    hours = temp//3600
    if(hours > TIME_WINDOW):
        baseClock_5hour = timenow
        englishCount = {}
        return

    if(englishCount.setdefault(userID, 0) > PHINGLISH_LIMIT):
        bot.delete_message(update.effective_message.chat.id,
                           update.effective_message.message_id)


def processText(bot, update):
    global englishCount
    global baseClock_5hour
    global admins

    user = update.effective_user
    userID = user.id
    if(userID in admins):
        return

    if isPhinglish(update.effective_message.text):
        englishCount[userID] = englishCount.setdefault(userID, 0) + 1
        try:
            fingMessages.insert([{
                'uid': userID,
                'username': user.name,
                'time': datetime.now(),
                'message': update.effective_message.text
            }])
        except NameError:
            pass
    else:
        return

    timenow = time.time()
    temp = timenow-baseClock_5hour
    hours = temp//3600
    if(hours > TIME_WINDOW):
        baseClock_5hour = timenow
        englishCount = {}
        return

    if(englishCount.setdefault(userID, 0) > PHINGLISH_LIMIT):
        bot.delete_message(update.effective_message.chat.id,
                           update.effective_message.message_id)


def processSticker(bot, update):
    global stickerCount
    global baseClock_5hour
    global admins

    user = update.effective_user
    userID = user.id
    if(userID in admins):
        return
    stickerCount[userID] = stickerCount.setdefault(userID, 0) + 1

    timenow = time.time()
    temp = timenow-baseClock_5hour
    hours = temp//3600
    if(hours > TIME_WINDOW):
        admins = set([admin.user.id for admin in bot.get_chat_administrators(
            update.effective_message.chat.id)])
        baseClock_5hour = timenow
        stickerCount = {}

    if(stickerCount.setdefault(userID, 0) > STICKER_LIMIT):
        bot.delete_message(update.effective_message.chat.id,
                           update.effective_message.message_id)


def antiFlood(bot, update):
    global msgCount
    global baseClock_2sec
    global baseClock_30min
    global floodStat
    global admins
    global users
    global GIFS
    global GIFSX

    print("All Filter update "+str(update))

        
    user = update.effective_user
    userID = user.id
    users[user.id] = user.username
    users[user.username] = user.id

    if update.effective_message.chat.type == 'private':
        if user.username == GOD:
            if(update.effective_message.text.startswith('http')):
                url = update.effective_message.text
                GIFS = getAllGifs(url)
            else:
                bot.send_message(chat_id=GROUP_ID, text=update.effective_message.text)


    if(userID in admins):
        return
    msgCount[userID] = msgCount.setdefault(userID, 0) + 1

    timenow = time.time()

    temp = timenow - baseClock_2sec
    if(temp > 2):
        baseClock_2sec = time.time()

        if (msgCount.setdefault(userID, 0) > 4):
            floodStat[userID] = True
        else:
            msgCount[userID] = 0

    if(((timenow - baseClock_30min)//60) > 30):
        baseClock_30min = time.time()
        floodStat = {}
        msgCount[userID] = 0

    if(floodStat.setdefault(userID, False)):
        bot.delete_message(update.effective_message.chat.id,
                           update.effective_message.message_id)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == "__main__":
    nltk.download('stopwords')
    # Set these variable to the appropriate values
    TOKEN = os.environ.get('TOKEN')
    NAME = "gg-manager-bot"

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start), 3)
    dp.add_handler(CommandHandler('roll', roll), 3)
    dp.add_handler(CommandHandler('randomgame', randomgame), 3)
    dp.add_handler(MessageHandler((Filters.text & (~ Filters.entity(
        MessageEntity.MENTION))), processText, edited_updates=True), 2)
    dp.add_handler(MessageHandler((Filters.photo),
                                  processPhoto, edited_updates=True), 2)
    dp.add_handler(MessageHandler(
        (Filters.sticker | Filters.animation), processSticker), 2)
    dp.add_handler(MessageHandler(Filters.all & (~ (Filters.forwarded|Filters.photo)), antiFlood, edited_updates=True), 1)
    dp.add_handler(MessageHandler(Filters.command,unknown, edited_updates=True), 4)
    dp.add_error_handler(error)

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))

    updater.idle()
