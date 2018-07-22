#!/usr/bin/env python3
# Copyright (c) 2018 Lyndros
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
import discord
import asyncio
import requests
import coinmarketcap
import json

from urllib.request         import urlopen
from discord.ext.commands   import Bot
from discord.ext            import commands
from datetime               import datetime
from prettytable            import PrettyTable

################################################################################
#                          CONFIGURATION PARAMETERS                            #
################################################################################
#COIN ACRONYM SUCH AS: BTC/TOK/EOS...
COIN_NAME       = "Tokugawa"
COIN_ACRONYM    = "TOK"
#URL TO EXPLORER COIN API EXAMPLE FOR TOKUGAWA, PLEASE MODIFY
COIN_EXPLORER_BASE_URL="http://explorer.tokugawacoin.com/ext/getaddress/"
#MASTERNODE: SETUP DATE, INITIAL COINS, ADDRESS
MASTERNODE_LIST = {
    "MN01": ("09/07/2018", 2500, "YOUR_ADDRESS"),
    "MN02": ("09/07/2018", 2500, "YOUR_ADDRESS"),
    "MN03": ("09/07/2018", 2500, "YOUR_ADDRESS"),
    "MN04": ("09/07/2018", 2500, "YOUR_ADDRESS")
}

#THESE ARE OTHER ADDRESSES SHOWN IN BALANCE BUT NOT MASTERNODES
OTHER_ADDRESS_LIST = {
    "PERS": "YOUR_ADDRESS"
}
#PRECISION IN DECIMALS TO BE SHOWN
DECIMALS=6
#DISCORD API KEY TO RUN MY BOT
DISCORD_API_KEY="YOUR_DISCORD_API_KEY"
################################################################################
Client = discord.Client()
client = commands.Bot(command_prefix = "!")

lista_comandos = {
  "AYUDA":        "Muestra esta ayuda.",
  "PRECIO":       "Muestra el precio actual de la moneda.",
  "BALANCE":      "Muestra un resumen el balance actual de los MNs.",
  "RENDIMIENTO":  "Muestra el precio actual de la moneda."
}

def get_running_days(date_epoch):
    #Starting date
    d0 = datetime.strptime(date_epoch, '%d/%m/%Y')
    #Current date
    d1 = datetime.strptime(datetime.now().strftime('%d/%m/%Y'),'%d/%m/%Y')
    delta = d1 - d0

    return delta.days

def get_balance(address):
    url = COIN_EXPLORER_BASE_URL + address
    req = requests.get(url)
    status_code = req.status_code
    if status_code == 200:
        #Limit to 6 decimals
        return round(float(json.loads(req.text)['balance']),DECIMALS)
    else:
        return None

def mostrar_ayuda():
    message="\n+Lista de comandos:\n"
    for comando in sorted(dict.keys(lista_comandos)):
        message+='*{0:14}'.format(comando)+lista_comandos[comando]+'\n'

    return message

def mostrar_precio():
    Now = datetime.now()
    market = coinmarketcap.Market()
    coin = market.ticker(COIN_NAME, convert="EUR")
    message = "\n+Marketcap " + COIN_ACRONYM + "(" + str('{:%d/%m/%Y - %H:%M:%S}'.format(datetime(Now.year, Now.month, Now.day, Now.hour, Now.minute, Now.second))) + ")" + \
    "\nRanking       = " + coin[0]['rank'] + \
    "\nPrecio EUR    = " + coin[0]['price_eur'] + " €" + \
    "\nPrecio BTC    = " + coin[0]['price_btc'] + \
    "\nMarketCap EUR = " + str('{:,.2f}'.format(float(coin[0]['market_cap_eur']))) + " €" + \
    "\n% cambio 1h   = " + coin[0]['percent_change_1h'] + " %" + \
    "\n% cambio 24h  = " + coin[0]['percent_change_24h'] + " %" + \
    "\n% cambio 7d   = " + coin[0]['percent_change_7d'] + " %"

    return message

def mostrar_balance():
    #Variable para calcular el balance total
    Total_Balance = 0

    #Construimos la dichosa tablita
    Tabla = PrettyTable()
    Tabla.field_names = ["MN", "Balance"]
    #Get balance for all nodes
    for mn in sorted(dict.keys(MASTERNODE_LIST)):
        MN_Current_Coins = get_balance(MASTERNODE_LIST[mn][2])
        Total_Balance += MN_Current_Coins
        Tabla.add_row([mn, MN_Current_Coins])
    #Get balance for other addresses
    for oaddr in sorted(dict.keys(OTHER_ADDRESS_LIST)):
        OADDR_Current_Coins = get_balance(OTHER_ADDRESS_LIST[oaddr])
        Total_Balance += OADDR_Current_Coins
        Tabla.add_row([oaddr, OADDR_Current_Coins])

    #Ponemos todo en el mensajito de vuelta
    message = '\n' + \
    '+Balance ' + COIN_ACRONYM +'\n' + \
    Tabla.get_string() + '\n'  \
    '- Total:       '+str(round(Total_Balance,DECIMALS))+" "+COIN_ACRONYM

    return message

def mostrar_rendimiento():
    #Coge el valor actual de la moneda
    market = coinmarketcap.Market()
    coin = market.ticker(COIN_NAME, convert="EUR")

    #Construimos la dichosa tablita
    Tabla = PrettyTable()
    Tabla.field_names = ["MN", "Balance", "TOK/Dia", "EUR/Dia"]
    #Get balance for all nodes
    for mn in sorted(dict.keys(MASTERNODE_LIST)):
        MN_Init_Date = MASTERNODE_LIST[mn][0]
        MN_Initial_Coins = MASTERNODE_LIST[mn][1]
        MN_Current_Coins = get_balance(MASTERNODE_LIST[mn][2])
        MN_Running_Days  = get_running_days(MN_Init_Date)
        MN_Coins_Day     = round((MN_Current_Coins-MN_Initial_Coins)/MN_Running_Days,DECIMALS)
        MN_EUR_Day       = round(MN_Coins_Day*float(coin[0]['price_eur']),DECIMALS)
        Tabla.add_row([mn, MN_Current_Coins, MN_Coins_Day, MN_EUR_Day])

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
    print(COIN_NAME + " BOT funcionando")

@client.event
async def on_message(message):
    if (message.content.upper()[0:5]=="/BOT "):
        return_message = comando_bot(message.content.upper()[5:])
        await client.send_message(message.channel, "```diff" + return_message + "\n```")

client.run(DISCORD_API_KEY)
