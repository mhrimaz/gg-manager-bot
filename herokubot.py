import logging
import os
import random
import datetime
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
from telegram import Message, User, Chat, MessageEntity, Document
from random import randint

games = ['R6','R6','R6', 'RL', 'RL', 'RL', 'Apex']
stickerCount = {}
englishCount = {}
msgCount = {}
floodStat = {}

baseClock_5hour = time.time()
baseClock_2sec = time.time()
baseClock_30min = time.time()



def unknown(bot, update):
    bot.delete_message(update.effective_message.chat.id, update.effective_message.message_id)



def start(bot, update):
    update.effective_message.reply_text("GG ?")

def randomgame(bot, update):
    update.effective_message.reply_text("GG "+ random.choice(games))
    
def roll(bot, update):
    update.effective_message.reply_text("GG "+ str(randint(0,100)))

def isEnglish(text):
    countEnglishLetters = 0
    for c in text:
        if ord(c) < 128 and c.isalpha():
            countEnglishLetters += 1
    return countEnglishLetters/len(text) >0.5

def processText(bot, update):
    global englishCount
    global baseClock_5hour
    
    user = update.effective_user
    username = user['username']
    
    if isEnglish(update.effective_message.text):
        englishCount[username] = englishCount.setdefault(username, 0) + 1
    
    
    
    timenow = time.time()
    temp = timenow-baseClock_5hour
    hours = temp//3600
    if(hours>5):
        baseClock_5hour = timenow
        englishCount = {}
        return
    
    if(englishCount.setdefault(username, 0)>10) and isEnglish(update.effective_message.text):
        bot.delete_message(update.effective_message.chat.id, update.effective_message.message_id)
    
    

def processSticker(bot, update):
    global stickerCount
    global baseClock_5hour
    print("sticker update "+str(update))
    
    user = update.effective_user
    username = user['username']
    
    stickerCount[username] = stickerCount.setdefault(username, 0) + 1
    
    
    timenow = time.time()
    temp = timenow-baseClock_5hour
    hours = temp//3600
    if(hours>5):
        baseClock_5hour = timenow
        stickerCount = {}
        
    if(stickerCount.setdefault(username, 0)>5):
        bot.delete_message(update.effective_message.chat.id, update.effective_message.message_id)

def antiFlood(bot, update):
    global msgCount
    global baseClock_2sec
    global baseClock_30min
    global floodStat
    
    print("All Filter update "+str(update))

    user = update.effective_user
    username = user['username']
    msgCount[username] = msgCount.setdefault(username, 0) + 1

    timenow = time.time()

    temp = timenow - baseClock_2sec
    if(temp > 2):
        baseClock_2sec = time.time()
        msgCount[username] = 0
        if (msgCount.setdefault(username, 0) > 10):
            floodStat[username] = True
        
    if(((timenow - baseClock_30min)//60)>30):
        baseClock_30min = time.time()
        floodStat = {}
        msgCount[username] = 0
        
    if(floodStat.setdefault(username, False) ):
        bot.delete_message(update.effective_message.chat.id, update.effective_message.message_id)
        

    
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = os.environ.get('TOKEN')
    NAME = "gg-manager-bot"


    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start), 3)
    dp.add_handler(CommandHandler('roll', roll), 3)
    dp.add_handler(CommandHandler('randomgame', randomgame), 3)
    dp.add_handler(MessageHandler((Filters.text & (~ Filters.entity(MessageEntity.MENTION))), processText, edited_updates=True), 2)
    dp.add_handler(MessageHandler((Filters.sticker | Filters.animation), processSticker), 2)
    dp.add_handler(MessageHandler(Filters.all, antiFlood, edited_updates=True),1)
    dp.add_handler(MessageHandler(Filters.command, unknown,edited_updates=True),4)
    dp.add_error_handler(error)

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    
    updater.idle()
