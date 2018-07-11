import discord
import asyncio
import requests
from urllib.request         import urlopen
from discord.ext.commands   import Bot
from discord.ext            import commands
import coinmarketcap
import json
from datetime               import datetime
from prettytable            import PrettyTable

Client = discord.Client()
client = commands.Bot(command_prefix = "!")

#SETUP PARAMETERS

lista_comandos = {
  "AYUDA":        "Muestra esta ayuda.",
  "PRECIO":       "Muestra el precio actual de la moneda.",
  "BALANCE":      "Muestra un resumen el balance actual de los MNs.",
  "RENDIMIENTO":  "Muestra el precio actual de la moneda."
}

def get_days(date_epoch):
    #Starting date
    d0 = datetime.strptime(date_epoch, '%d/%m/%Y')
    #Current date
    d1 = datetime.strptime(datetime.now().strftime('%d/%m/%Y'),'%d/%m/%Y')
    delta = d1 - d0

    return delta.days

def get_tok_balance(masternode_address):
    url = "http://explorer.tokugawacoin.com/ext/getaddress/"+masternode_address
    req = requests.get(url)
    status_code = req.status_code
    if status_code == 200:
        #Limit to 6 decimals
        return round(float(json.loads(req.text)['balance']),6)
    else:
        return None

def mostrar_ayuda():
    message="\n+Lista de comandos:\n"
    for comando in dict.keys(lista_comandos):
        message+='*{0:14}'.format(comando)+lista_comandos[comando]+'\n'

    return message

def mostrar_precio():
    Now = datetime.now()
    market = coinmarketcap.Market()
    coin = market.ticker("tokugawa", convert="EUR")
    message = 	"\n+Marketcap TOK (" + str('{:%d/%m/%Y - %H:%M:%S}'.format(datetime(Now.year, Now.month, Now.day, Now.hour, Now.minute, Now.second))) + ")" + \
    "\nRanking       = " + coin[0]['rank'] + \
    "\nPrecio EUR    = " + coin[0]['price_eur'] + " €" + \
    "\nPrecio BTC    = " + coin[0]['price_btc'] + \
    "\nMarketCap EUR = " + str('{:,.2f}'.format(float(coin[0]['market_cap_eur']))) + " €" + \
    "\n% cambio 1h   = " + coin[0]['percent_change_1h'] + " %" + \
    "\n% cambio 24h  = " + coin[0]['percent_change_24h'] + " %" + \
    "\n% cambio 7d   = " + coin[0]['percent_change_7d'] + " %"

    return message

def mostrar_balance():
    #Get balance for all nodes
    Balance_MN01 = get_tok_balance('ADDRESS_MN01')
    Balance_MN02 = get_tok_balance('ADDRESS_MN02')

    #Construimos la dichosa tablita
    Tabla = PrettyTable()
    Tabla.field_names = ["Masternode", "Balance"]
    Tabla.add_row(["MN01", Balance_MN01])
    Tabla.add_row(["MN02", Balance_MN02])

    #Ponemos todo en el mensajito de vuelta
    message = '\n' + \
    '+Balance TOK\n' + \
    Tabla.get_string() + '\n'  \
    '- Total:       '+str(round(Balance_MN01+Balance_MN02,6))

    return message

def mostrar_rendimiento():
    #Get the balance from toku explorer
    Balance_MN01 = get_tok_balance('ADDRESS_MN01')
    Balance_MN02 = get_tok_balance('ADDRESS_MN02')

    #Initial setup dates
    Running_Days_MN01 = get_days('04/03/2018')
    Running_Days_MN02 = get_days('12/03/2018')

    #Media de TOK por dia
    Coins_Day_MN01 = round((Balance_MN01-2500)/Running_Days_MN01,6)
    Coins_Day_MN02 = round((Balance_MN02-2500)/Running_Days_MN02,6)

    #Coge el valor actual de la moneda
    market = coinmarketcap.Market()
    coin = market.ticker("tokugawa", convert="EUR")

    #Valor en euros
    EUR_Day_MN01=round(Coins_Day_MN01*float(coin[0]['price_eur']),6)
    EUR_Day_MN02=round(Coins_Day_MN02*float(coin[0]['price_eur']),6)

    #Construimos la dichosa tablita
    Tabla = PrettyTable()
    Tabla.field_names = ["Masternode", "Balance", "TOK/Dia", "EUR/Dia"]
    Tabla.add_row(["MN01", Balance_MN01, Coins_Day_MN01, EUR_Day_MN01])
    Tabla.add_row(["MN02", Balance_MN02, Coins_Day_MN02, EUR_Day_MN02])

    #Ponemos todo en el mensajito de vuelta
    message = "\n" + \
    "+Rendimiento MNs\n" + \
    Tabla.get_string()

    return message

def comando_bot(cmd):
    if   (cmd == "AYUDA"):
        message = mostrar_ayuda()
    elif (cmd == "PRECIO"):
        message = mostrar_precio()
    elif (cmd == "BALANCE"):
        message = mostrar_balance()
    elif (cmd == "RENDIMIENTO"):
        message =  mostrar_rendimiento()
    else:
        message = "\n-Error! Comando desconocido.\nTeclee '/bot ayuda' para mostrar una lista de los comandos disponibles."

    return message

@client.event
async def on_ready():
    print("BOT funcionando")

@client.event
async def on_message(message):
    if (message.content.upper()[0:5]=="/BOT "):
        return_message = comando_bot(message.content.upper()[5:])
        await client.send_message(message.channel, "```diff" + return_message + "\n```")

client.run("DISCORD_API_KEY")
