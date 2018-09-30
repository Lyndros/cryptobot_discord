#!/usr/bin/env python3
# Copyright (c) 2018 Lyndros <lyndros@hotmail.com>
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

###################################################################
# If you want o support this repository I accept donations        #
# even 1 TOK is always welcome :-)!                               #
# > ethereum address: 0x44F102616C8e19fF3FED10c0b05B3d23595211ce  #
# > tokugawa address: TjrQBaaCPoVW9mPAZHPfVx9JJCq7yZ7QnA          #
###################################################################
import discord
import requests
import coinmarketcap
import json
import yaml
import argparse

from urllib.request         import urlopen
from discord.ext.commands   import Bot
from discord.ext            import commands
from datetime               import datetime
from prettytable            import PrettyTable

def justify_text_fix (string, width=None):
    #Define default separation to 10 if width
    SepWidth = 10 if (width==None) else width
    SepChar  = ' '

    #Initialise returning string
    new_string = '\n'

    for line in string.splitlines():
        for word in line.split():
            new_string+=word.ljust(SepWidth,SepChar)

        new_string += '\n'

    #print("Justified fix(%s): %s" %(SepWidth, new_string))

    return new_string

def justify_text_dyn (string):
    #Define minimun separation between fields
    min_separation=2

    #Init the maximum word lenght
    max_word_width=0
    for word in string.split():
        if len(word) > max_word_width:
            max_word_width = len(word)

    #Define the separation
    total_separation = max_word_width+min_separation

    #Get the text justified with the proper separation
    new_string = justify_text_fix(string, width=total_separation)

    #print("Justified dyn(%s): %s" %(total_separation, new_string))

    return new_string

def get_running_days(date_epoch):
    #Starting date
    d0 = datetime.strptime(date_epoch, '%d/%m/%Y')
    #Current date
    d1 = datetime.strptime(datetime.now().strftime('%d/%m/%Y'),'%d/%m/%Y')
    delta = d1 - d0

    return delta.days

def get_balance(address):
    #Read balance from local file
    if CONFIG['COIN']['explorer_url'][0:7]=='file://':
        with open(CONFIG['COIN']['explorer_url'][7:]) as balance_file:
            for line in balance_file:
                wallet_address, balance = line.split()
                if wallet_address==address:
                    #LOKI PATCH WE NEED TO REDUCE COLLATERAL
                    if CONFIG['COIN']['acronym'] == 'LOKI':
                        return round(float(balance)-float(CONFIG['COIN']['collateral']),CONFIG['COIN']['decimals'])
                    else:
                        return round(float(balance), CONFIG['COIN']['decimals'])

    #Get value from explorer
    else:
        url = CONFIG['COIN']['explorer_url'] + address
        req = requests.get(url)
        status_code = req.status_code
        if status_code == 200:
            #Limit to decimals
            return round(float(json.loads(req.text)['balance']),CONFIG['COIN']['decimals'])

    #Return none if not found
    return None

def get_coinmarketcap_id(coin_acronym):
    #Request coin listing to coinmarket cap
    request = requests.get('https://api.coinmarketcap.com/v2/listings/')
    results = request.json()

    #Search for the id
    for coin in results["data"]:
        if coin["symbol"].upper() == coin_acronym.upper():
            return int(coin["id"])

def get_coinmarketcap_stats(coin_acronym):
    # Retrieve coinmarketcap id (comment o avoid recurrent calls, done in config)
    # coin_id = get_coinmarketcap_id(CONFIG['COIN']['acronym'])

    # Get specific coin data
    request = requests.get('https://api.coinmarketcap.com/v2/ticker/' + str(CONFIG['COIN']['id']) + "/?convert=EUR")
    coin_data = request.json()

    return coin_data

def mostrar_ayuda():
    # Declare embed object
    embed       = discord.Embed()
    embed.color = CONFIG['STYLE']['FRAME']['default_color']
    embed.set_thumbnail(url='https://s2.coinmarketcap.com/static/img/coins/32x32/%s' %CONFIG['COIN']['id']  + '.png')

    embed.title = "**__LISTA DE COMANDOS__**"

    for comando in sorted(dict.keys(LISTA_COMANDOS)):
        embed.add_field(name="- "+comando.capitalize(), value="*"+LISTA_COMANDOS[comando]+"*", inline=False)

    return embed

def mostrar_precio():
    # Declare embed object
    embed       = discord.Embed()
    embed.color = CONFIG['STYLE']['FRAME']['default_color']
    embed.set_thumbnail(url='https://s2.coinmarketcap.com/static/img/coins/32x32/%s' %CONFIG['COIN']['id']  + '.png')
    embed.title = "**__PRECIO DE %s (%s)__**" %(CONFIG['COIN']['name'].upper(), CONFIG['COIN']['acronym'].upper())
    embed.url   = 'https://coinmarketcap.com/currencies/' + CONFIG['COIN']['name'] + '/'

    try:
        #Read coin stats from coinmarketcap
        coin_stats = get_coinmarketcap_stats(CONFIG['COIN']['acronym'])

        embed.description = "**Ranking:**        " + str('{:,.0f}'.format(coin_stats['data']['rank'])) + "\n" + \
                            "\n**Precio EUR**:     " + str('{:,.8f}'.format(float(coin_stats['data']['quotes']['EUR']['price']))) + " €" + \
                            "\n**Precio USD**:     " + str('{:,.8f}'.format(float(coin_stats['data']['quotes']['USD']['price']))) + " $" + \
                            "\n**MarketCap EUR**:  " + str('{:,.0f}'.format(float(coin_stats['data']['quotes']['EUR']['market_cap']))) + " €" + \
                            "\n**Volum 24h EUR**:  " + str('{:,.0f}'.format(float(coin_stats['data']['quotes']['EUR']['volume_24h']))) + " €" + \
                            "\n**Emision Actual**: " + str('{:,.0f}'.format(float(coin_stats['data']['total_supply']))) + " " + coin_stats['data']['symbol'] + "\n" + \
                            "\n**Cambio 1h **:     " + str(coin_stats['data']['quotes']['EUR']['percent_change_1h']) + "%" + \
                            "\n**Cambio 24h**:     " + str(coin_stats['data']['quotes']['EUR']['percent_change_24h']) + \
                            "\n**Cambio 7d **:     " + str(coin_stats['data']['quotes']['EUR']['percent_change_7d']) + "%"

        embed.set_footer(text="coinmarketcap @%s" %coin_stats['metadata']['timestamp'], icon_url="https://logo.clearbit.com/coinmarketcap.com")

    except:
        embed.color = CONFIG['STYLE']['FRAME']['error_color']
        embed.description = "Error leyendo datos de coinmarketcap."

    return embed

def mostrar_balance():
    #Declare embed object
    embed       = discord.Embed()
    embed.color = CONFIG['STYLE']['FRAME']['default_color']
    #embed.set_thumbnail(url='https://s2.coinmarketcap.com/static/img/coins/32x32/%s' %CONFIG['COIN']['id']  + '.png')

    embed.title = "**__BALANCE__**"

    #Variable para calcular el balance total
    Total_Balance = 0.0

    #Init description
    embed.description = ""

    #Get balance for all nodes
    my_addresses = CONFIG['MASTERNODES'] if ('MASTERNODES' in CONFIG.keys()) else [];
    for mn in my_addresses:
        MN_Current_Coins = get_balance(mn['address'])
        Total_Balance += MN_Current_Coins

        #This is working
        embed.description += mn['name'] + " {0:.{1}f}".format(MN_Current_Coins, CONFIG['COIN']['decimals']) + '\n'

    #Get balance for other addresses
    my_addresses = CONFIG['OTHER_ADDRESSES'] if ('OTHER_ADDRESSES' in CONFIG.keys()) else [];
    for oaddr in my_addresses:
        OADDR_Current_Coins = get_balance(oaddr['address'])
        Total_Balance += OADDR_Current_Coins

        #This is working
        embed.description += oaddr['name'] + " {0:.{1}f}".format(OADDR_Current_Coins, CONFIG['COIN']['decimals']) + '\n'

    #End the description
    embed.description +='TOTAL: ' + "{0:.{1}f}".format(Total_Balance, CONFIG['COIN']['decimals']) + ' ' + CONFIG['COIN']['acronym']

    embed.description = '```'+justify_text_dyn(embed.description)+'```'

    return embed

def mostrar_rendimiento():
    #Declare embed object
    embed       = discord.Embed()
    embed.color = CONFIG['STYLE']['FRAME']['default_color']
    #embed.set_thumbnail(url='https://s2.coinmarketcap.com/static/img/coins/32x32/%s' %CONFIG['COIN']['id']  + '.png')

    embed.title = "**__RENDIMIENTO MNs__**"

    #Coge el valor actual de la moneda
    coin_stats = get_coinmarketcap_stats(CONFIG['COIN']['acronym'])

    #Para calcular el total
    Total_EUR_Day   = 0.0
    Total_Coins_Day = 0.0

    #Init the description message
    embed.description= "MN " + CONFIG['COIN']['acronym']+"/Dia €/Dia\n"

    #Get balance for all nodes
    my_addresses = CONFIG['MASTERNODES'] if ('MASTERNODES' in CONFIG.keys()) else [];
    for mn in my_addresses:
        MN_Init_Date     = mn['setup_date']
        MN_Initial_Coins = mn['setup_balance']
        MN_Current_Coins = get_balance(mn['address'])
        MN_Running_Days  = get_running_days(MN_Init_Date)+1
        MN_Coins_Day     = round((MN_Current_Coins-MN_Initial_Coins)/MN_Running_Days, CONFIG['COIN']['decimals'])
        MN_EUR_Day       = round(MN_Coins_Day*float(coin_stats["data"]['quotes']["EUR"]["price"]), CONFIG['COIN']['decimals'])
        embed.description += mn['name'] + " {0:.{1}f}".format(MN_Coins_Day, CONFIG['COIN']['decimals']) + " {0:.{1}f}".format(MN_EUR_Day, 2) + '\n'

        Total_EUR_Day    += MN_EUR_Day
        Total_Coins_Day  += MN_Coins_Day

    #End the description
    embed.description += 'TOTAL: ' + "{0:.{1}f}".format(Total_Coins_Day, CONFIG['COIN']['decimals']) + ' ' + "{0:.{1}f}".format(Total_EUR_Day, 2) + '\n'

    embed.description = '```'+justify_text_dyn(embed.description)+'```'

    return embed

def mostrar_inversores():
    # Declare embed object
    embed       = discord.Embed()
    embed.color = CONFIG['STYLE']['FRAME']['default_color']
    #embed.set_thumbnail(url='https://s2.coinmarketcap.com/static/img/coins/32x32/%s' %CONFIG['COIN']['id']  + '.png')

    embed.title = "**__INVERSORES__**"

    #Variable para calcular el total minado
    Total_Mined = 0.0

    #Init the message description
    embed.description = ""

    #Get balance for all nodes
    my_addresses = CONFIG['MASTERNODES'] if ('MASTERNODES' in CONFIG.keys()) else [];
    for mn in my_addresses:
        MN_Current_Coins = get_balance(mn['address'])
        MN_Total_Mined   = MN_Current_Coins - float(mn['setup_balance'])

        embed.description+= mn['name'] + '\n'
        embed.description+= "Nombre(%) Generado Total\n"

        # Construimos la dichosa tablita
        #Tabla = PrettyTable()
        #Tabla.padding_width = 0
        #Tabla.field_names = ['Nombre', '(%)', 'Mined', 'Deposito+Mined']

        # Get expenses for current masternode
        my_expenses = mn['EXPENSES'] if ('EXPENSES' in mn.keys()) else [];
        MN_Total_Expenses = 0;
        for exp in my_expenses:
            MN_Total_Expenses += exp['coins']

        #Calculate total expenses
        MN_Total_Expenses = MN_Total_Expenses + (MN_Total_Mined*mn['operator'])

        #Get total generated by MN after deducting expenses
        MN_Generated = MN_Total_Mined - MN_Total_Expenses

        # Get inverstors for current masternode
        my_investors = mn['INVESTORS'] if ('INVESTORS' in mn.keys()) else [];
        #Loop through all investors for current MN
        for inv in my_investors:
            inv_percent   = (float(inv['coins'])/float(CONFIG['COIN']['collateral']))*100.0
            inv_generated = float(MN_Generated)*(inv_percent/100.0)
            inv_total     = float(inv['coins']) + inv_generated

            #Dump investor information
            embed.description+= inv['name'] + "({0:.{1}f}%)".format(inv_percent, 0) + " {0:.{1}f}".format(inv_generated, CONFIG['COIN']['decimals']) + " {0:.{1}f}".format(inv_total, CONFIG['COIN']['decimals']) + '\n'

            #Tabla.add_row([inv['name'], "{0:.{1}f}".format(inv_percent, 2),
            #              "{0:.{1}f}".format(inv_generated, CONFIG['COIN']['decimals']),
            #               "{0:.{1}f}".format(inv_total, CONFIG['COIN']['decimals'])])

        #Store a total variable containing the total mined by all masternodes
        Total_Mined += MN_Total_Mined

        embed.description += '\n'
        embed.description += "Gastos:" + " {0:.{1}f}".format(MN_Total_Expenses, 1) + " (%s%%)" %(int(mn['operator']*100)) + '\n'
        embed.description += "Generado:" + " {0:.{1}f}".format(MN_Generated, 1) + '\n'

        # Separate MASTERNODEs
        embed.description += '\n'
        #embed.description += '\n'+ Tabla.get_string() + '\n'

    embed.description = '```' + justify_text_dyn(embed.description) + '```'

    #embed.set_footer(text='Total mined: ' + "{0:.{1}f}".format(Total_Mined, CONFIG['COIN']['decimals']) + ' ' + CONFIG['COIN']['acronym'])

    return embed

def comando_bot(cmd):
    if   (cmd == "AYUDA"):
        embed_message = mostrar_ayuda()
    elif (cmd == "PRECIO"):
        embed_message = mostrar_precio()
    elif (cmd == "BALANCE"):
        embed_message = mostrar_balance()
    elif (cmd == "INVERSORES"):
        embed_message = mostrar_inversores()
    elif (cmd == "RENDIMIENTO"):
        embed_message =  mostrar_rendimiento()
    else:
        # Declare embed object
        embed_message       = discord.Embed()
        embed_message.color = CONFIG['STYLE']['FRAME']['error_color']
        embed_message.title = "**__ERROR__**"
        embed_message.description = "Teclee '/bot ayuda' para mostrar una lista de los comandos disponibles."

    return embed_message

#Define global var to store the list of supported commands
LISTA_COMANDOS = {
  "AYUDA":              "Muestra esta ayuda",
  "PRECIO":             "Muestra el precio actual de la moneda",
  "BALANCE":            "Muestra el balance actual total",
  "INVERSORES":         "Muestra el balance de los inversores",
  "RENDIMIENTO":        "Muestra el rendimiendo actual de los MNs",
}

#Tested in iPhone 6S this is the maximum length per string
MAX_MOBILE_STRLEN = 43

#Parse program parameters
parser = argparse.ArgumentParser()
parser.add_argument("config_file", help="The configuration file to be loaded.")
args = parser.parse_args()

#Parse configuration file
with open(args.config_file, 'r') as ymlfile:
    CONFIG = yaml.load(ymlfile)
    #Store the coin ID at the beginning to avoid recurrent calls to coinmarketcap
    CONFIG['COIN']['id'] = get_coinmarketcap_id(CONFIG['COIN']['acronym'])

#Start the discord client
Client = discord.Client()
client = commands.Bot(command_prefix = "!")

@client.event
async def on_ready():
    print(CONFIG['COIN']['name'] + " BOT funcionando")

@client.event
async def on_message(message):
    if (message.content.upper()[0:5]=="/BOT "):
        embed_message = comando_bot(message.content.upper()[5:])
        await client.send_message(message.channel, embed=embed_message)

client.run(CONFIG['DISCORD']['api_key'])