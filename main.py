import logging
from datetime import date
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello")

async def currencies_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # This function send information about cryptocurrency
    # 1. Get information about cryptocurrency
    async with aiohttp.ClientSession() as session:
        currencies_rates_url = 'https://api.coingecko.com/api/v3/exchange_rates'
        async with session.get(currencies_rates_url) as resp:
            currencies_rates = await resp.json()
            currency = str(currencies_rates)
            print(currencies_rates)
            btc = currencies_rates["rates"]["btc"]
            eth = currencies_rates["rates"]["eth"]
            result = {"btc": btc, "eth": eth}
            currency_result = str(result)
    # 2. Send information to user
            await context.bot.send_message(chat_id=update.effective_chat.id, text=currency_result)

async def money_currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function will be show information about currencies of real money
    # 1. Get information about currencies
    async with aiohttp.ClientSession() as session:
        money_currencies_url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
        today = date.today()
        d1 = today.strftime("%d.%m.%Y")
        d2 = money_currencies_url+d1
        async with session.get(d2) as resp:
            money_currencies = await resp.json()
            rates = money_currencies["exchangeRate"]
            result = []
            for rate in rates:
                formatted = "Base Currency {}, Currency {}, Sale Rate {}, Purchase Rate {}".format(rate["baseCurrency"], rate["currency"], rate["saleRateNB"], rate["purchaseRateNB"])
                result.append(formatted)
            money_result = "\n ".join(result)
    # 2. Send information to user
            await context.bot.send_message(chat_id=update.effective_chat.id, text=money_result)

# Show weather in city
async def show_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function will be show weather on current time in city
    # 1. Get information about weather in city
    async with aiohttp.ClientSession() as session:
        api_key = "0c3a23b3418374fa864f71bcf3d5e018"
        city = update.message.text.split()[1]
        print(city)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
        async with session.get(url) as resp:
            show_weather = await resp.json()
            weather_result = " Lon {}, Latitude {}, \n Temparature {}, \n Pressure {}, \n Wind Speed {}, \n Name {}".format(
                show_weather["coord"]["lon"], show_weather["coord"]["lat"], show_weather["main"]["temp"], show_weather["main"]["pressure"], show_weather["wind"]["speed"], show_weather["name"])
    # 2. Send information user
            await context.bot.send_message(chat_id=update.effective_chat.id, text=weather_result)

# This will show what Command has Bot
async def commands_line (update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function will be show list of the command to user
    commands_line = """CryptoCurrenciesBot Commands:
    1. /commands - show you list of the commands in that Bot
    2. /currencies_rates - show you currencies in current time of BTC and ETH
    3. /money_currencies - show you currencies of real money in current time
    4. /show_weather - show you weather in current time of the city which you want (notice: add your city after command)
    5. /get_contacts - show you list of your contacts
    6. /add_contact - add contact to your phonebook (notice: must be name and phone number)
    7. /delete_contact - deleting contact which you want"""
    # Send information to user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=commands_line)

#Link to my MongoDB database
uri = "mongodb+srv://pavlokulka:12345qwert@cluster0.bgu4ah3.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))

# This will add contact to your phonebook
async def add_contact (update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function will be add contact to your phonebook
    contact = update.message.text.split()[1]
    number = update.message.text.split()[2]
    document = {'contact': contact, "number": number, "user_id": update.effective_user.id}
    await client.telegram.phone_book.insert_one(document)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Contact was create")

# This function will show list of your contacts
async def get_contacts (update: Update, context:ContextTypes.DEFAULT_TYPE):
    find = client.telegram.phone_book.find({"user_id": update.effective_user.id})
    find_result = ["Contact name {}, Phone number {}".format(document["contact"], document['number']) async for document in find]
    convert = "\n".join(find_result)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=convert)

# This function will be delete contact
async def delete_contact (update: Update, context:ContextTypes.DEFAULT_TYPE):
    name = update.message.text.split()[1]
    await client.telegram.phone_book.delete_one({"user_id": update.effective_user.id, "contact": name})
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Contact succefully delete")



if __name__ == '__main__':
    application = ApplicationBuilder().token('6317225374:AAFe2L_CdrdvHpd0nXjv0dsznRoZwKXnNLs').build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    hellohandler = CommandHandler('hello', hello)
    application.add_handler(hellohandler)

    currencieshandler = CommandHandler('currencies_rates', currencies_rates)
    application.add_handler(currencieshandler)

    moneyhandler = CommandHandler('money_currencies', money_currencies)
    application.add_handler(moneyhandler)

    weatherhandler = CommandHandler('show_weather', show_weather)
    application.add_handler(weatherhandler)

    commandhandler = CommandHandler('commands', commands_line)
    application.add_handler(commandhandler)

    addcontacthandler = CommandHandler('add_contact', add_contact)
    application.add_handler(addcontacthandler)

    getcontactshandler = CommandHandler('get_contacts', get_contacts)
    application.add_handler(getcontactshandler)

    deletecontacthandler = CommandHandler('delete_contact', delete_contact)
    application.add_handler(deletecontacthandler)


    application.run_polling()

