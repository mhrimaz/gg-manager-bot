import logging
import os
import random
import datetime
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from random import randint

games = ['R6', 'RL', 'Apex', '''Don't play FoxHole!''']
stickerCount = {}
englishCount = {}
timecur = time.time()


def start(bot, update):
    update.message.reply_text("GG ?")

def randomgame(bot, update):
    update.message.reply_text("GG "+ random.choice(games))
    
def roll(bot, update):
    update.message.reply_text("GG "+ str(randint(0,100)))

def isEnglish(text):
    countEnglishLetters = 0
    for c in text:
        if ord(c) < 128 and c.isalpha():
            countEnglishLetters += 1
    return countEnglishLetters/len(text) >0.5

def processText(bot, update):
    logger.debug('user name'+ str(update.effective_user)) 
    user = update.effective_user
    username = user['username']
    logger.debug('user name'+ str(username)) 
    logger.debug('update.message.text '+ update.message.text + 'isenglish: '+str(isEnglish(update.message.text)))     
    if isEnglish(update.message.text):
        englishCount[username] = englishCount.setdefault(username, 0) + 1
    logger.debug('englishCount '+str(englishCount))  
    
    
    timenow = time.time()
    hours, rem = divmod(timecur-timenow, 3600)
    if(hours>5):
        timecur = timenow
        stickerCount = {}
        englishCount = {}
    
    if(englishCount[username]>10):
        bot.delete_message(update.message.chat.id, update.message.message_id)
    
    #update.effective_message.reply_text(update.effective_message.text)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = os.environ.get('TOKEN')
    NAME = "gg-manager-bot"

    stickerCount = {}
    englishCount = {}

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('roll', roll))
    dp.add_handler(CommandHandler('randomgame', randomgame))
    dp.add_handler(MessageHandler(Filters.text, processText))
    dp.add_error_handler(error)

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    
    updater.idle()
