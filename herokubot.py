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

games = ['R6', 'R6', 'R6', 'RL', 'RL', 'RL', 'Apex']
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


def unknown(bot, update):
    global admins
    global users
    global englishCount
    global msgCount
    global stickerCount
    global floodStat
    
    user = update.effective_user
    userID = user.id
    command = update.effective_message.text
    if(userID in admins):
        toForgive = users.setdefault([str(command[command.find('@')+1:])],"")
        stickerCount[toForgive] = 0
        englishCount[toForgive] = 0
        msgCount[toForgive] = 0
        floodStat[toForgive] = False
    print("command : " + )
    
    
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
    userNameToUserId[user.id]
    if(userID in admins):
        return
        
    if isPhinglish(update.effective_message.caption):
        englishCount[userID] = englishCount.setdefault(userID, 0) + 1    
    else:
        return
    
    timenow = time.time()
    temp = timenow-baseClock_5hour
    hours = temp//3600
    if(hours > 5):
        baseClock_5hour = timenow
        englishCount = {}
        return

    if(englishCount.setdefault(userID, 0) > 10) :
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
    else:
        return
        
    timenow = time.time()
    temp = timenow-baseClock_5hour
    hours = temp//3600
    if(hours > 5):
        baseClock_5hour = timenow
        englishCount = {}
        return

    if(englishCount.setdefault(userID, 0) > 10):
        bot.delete_message(update.effective_message.chat.id,
                           update.effective_message.message_id)


def processSticker(bot, update):
    global stickerCount
    global baseClock_5hour
    global admins

    print("sticker update "+str(update))

    user = update.effective_user
    userID = user.id
    if(userID in admins):
        return
    stickerCount[userID] = stickerCount.setdefault(userID, 0) + 1

    timenow = time.time()
    temp = timenow-baseClock_5hour
    hours = temp//3600
    if(hours > 5):
        admins = set([admin.user.id for admin in bot.get_chat_administrators(
            update.effective_message.chat.id)])
        baseClock_5hour = timenow
        stickerCount = {}

    if(stickerCount.setdefault(userID, 0) > 5):
        bot.delete_message(update.effective_message.chat.id,
                           update.effective_message.message_id)


def antiFlood(bot, update):
    global msgCount
    global baseClock_2sec
    global baseClock_30min
    global floodStat
    global admins
    global users

    print("All Filter update "+str(update))

    user = update.effective_user
    userID = user.id
    users[user.id] = user.username
    users[user.username] = user.id
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
    dp.add_handler(MessageHandler((Filters.photo), processPhoto, edited_updates=True), 2)
    dp.add_handler(MessageHandler(
        (Filters.sticker | Filters.animation), processSticker), 2)
    dp.add_handler(MessageHandler(
        Filters.all, antiFlood, edited_updates=True), 1)
    dp.add_handler(MessageHandler(Filters.command,
                                  unknown, edited_updates=True), 4)
    dp.add_error_handler(error)

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))

    updater.idle()
