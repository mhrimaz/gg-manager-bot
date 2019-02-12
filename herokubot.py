import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from random import randint

def start(bot, update):
    update.message.reply_text("GG ?")

def randomgame(bot, update):
    update.message.reply_text("GG R6")
    
def roll(bot, update):
    update.message.reply_text("GG "+str(randint(0,100))


#def echo(bot, update):
    #update.effective_message.reply_text(update.effective_message.text)

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
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('roll', roll))
    dp.add_handler(CommandHandler('randomgame', randomgame))
	
    dp.add_error_handler(error)

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    
    # Start the Bot
    #updater.start_polling()
    updater.idle()
