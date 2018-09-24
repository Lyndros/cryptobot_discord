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

#Add the configuration file to our python program
parser = argparse.ArgumentParser()
parser.add_argument("config_file", help="The configuration file to be loaded.")
args = parser.parse_args()

#Parse the configuration file
with open(args.config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

Client = discord.Client()
client = commands.Bot(command_prefix = "!")

lista_comandos = {
  "AYUDA":              "Muestra esta ayuda",
  "PRECIO":             "Muestra el precio actual de la moneda",
  "BALANCE":            "Muestra el balance actual de total de cuentas",
  "INVERSORES":         "Muestra el balance de los inversores",
  "RENDIMIENTO":        "Muestra el rendimiendo actual de los MNs",
}

def get_running_days(date_epoch):
    #Starting date
    d0 = datetime.strptime(date_epoch, '%d/%m/%Y')
    #Current date
    d1 = datetime.strptime(datetime.now().strftime('%d/%m/%Y'),'%d/%m/%Y')
    delta = d1 - d0

    return delta.days

def get_balance(address):
    #Read balance from local file
    if cfg['COIN']['explorer_url'][0:7]=='file://':
        with open(cfg['COIN']['explorer_url'][7:]) as balance_file:
            for line in balance_file:
                wallet_address, balance = line.split()
                if wallet_address==address:
                    #LOKI PATCH WE NEED TO REDUCE COLLATERAL
                    if cfg['COIN']['acronym'] == 'LOKI':
                        return round(float(balance)-float(cfg['COIN']['collateral']),cfg['COIN']['decimals'])
                    else:
                        return round(float(balance), cfg['COIN']['decimals'])

    #Get value from explorer
    else:
        url = cfg['COIN']['explorer_url'] + address
        req = requests.get(url)
        status_code = req.status_code
        if status_code == 200:
            #Limit to decimals
            return round(float(json.loads(req.text)['balance']),cfg['COIN']['decimals'])

    #Return none if not found
    return None

def mostrar_ayuda():
    message="\n+Lista de comandos:\n"
    for comando in sorted(dict.keys(lista_comandos)):
        message+='*{0:14}'.format(comando)+lista_comandos[comando] + '\n'

    return message

def mostrar_precio():
    Now = datetime.now()
    market = coinmarketcap.Market()
    coin = market.ticker(cfg['COIN']['name'], convert="EUR")
    message = "\n+Marketcap " + cfg['COIN']['acronym'] + "(" + str('{:%d/%m/%Y - %H:%M:%S}'.format(datetime(Now.year, Now.month, Now.day, Now.hour, Now.minute, Now.second))) + ")" + \
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
    Total_Balance = 0.0

    #Construimos la dichosa tablita
    Tabla = PrettyTable()
    Tabla.padding_width = 0
    Tabla.field_names = ["MN", "Balance"]

    #Get balance for all nodes
    my_addresses = cfg['MASTERNODES'] if ('MASTERNODES' in cfg.keys()) else [];
    for mn in my_addresses:
        MN_Current_Coins = get_balance(mn['address'])
        Total_Balance += MN_Current_Coins
        Tabla.add_row([mn['name'], "{0:.{1}f}".format(MN_Current_Coins, cfg['COIN']['decimals'])])

    #Get balance for other addresses
    my_addresses = cfg['OTHER_ADDRESSES'] if ('OTHER_ADDRESSES' in cfg.keys()) else [];
    for oaddr in my_addresses:
        OADDR_Current_Coins = get_balance(oaddr['address'])
        Total_Balance += OADDR_Current_Coins
        Tabla.add_row([oaddr['name'], "{0:.{1}f}".format(OADDR_Current_Coins, cfg['COIN']['decimals'])])

    #Ponemos todo en el mensajito de vuelta
    message = '\n+Balance General\n' + \
    Tabla.get_string() + '\n'  \
    '-Total: ' + "{0:.{1}f}".format(Total_Balance, cfg['COIN']['decimals']) + ' ' + cfg['COIN']['acronym'] + '\n'

    return message

def mostrar_rendimiento():
    #Coge el valor actual de la moneda
    market = coinmarketcap.Market()
    coin = market.ticker(cfg['COIN']['name'], convert="EUR")

    #Para calcular el total
    Total_EUR_Day   = 0.0
    Total_Coins_Day = 0.0

    #Construimos la dichosa tablita
    Tabla = PrettyTable()
    Tabla.padding_width = 0
    Tabla.field_names = ["MN", cfg['COIN']['acronym']+"/Dia", "€/Dia"]

    #Get balance for all nodes
    my_addresses = cfg['MASTERNODES'] if ('MASTERNODES' in cfg.keys()) else [];
    for mn in my_addresses:
        MN_Init_Date     = mn['setup_date']
        MN_Initial_Coins = mn['setup_balance']
        MN_Current_Coins = get_balance(mn['address'])
        MN_Running_Days  = get_running_days(MN_Init_Date)+1
        MN_Coins_Day     = round((MN_Current_Coins-MN_Initial_Coins)/MN_Running_Days, cfg['COIN']['decimals'])
        MN_EUR_Day       = round(MN_Coins_Day*float(coin[0]['price_eur']), cfg['COIN']['decimals'])
        Tabla.add_row([mn['name'], "{0:.{1}f}".format(MN_Coins_Day, cfg['COIN']['decimals']), "{0:.{1}f}".format(MN_EUR_Day, 2)])
        #Total Computation
        Total_EUR_Day    += MN_EUR_Day
        Total_Coins_Day  += MN_Coins_Day

    #Ponemos todo en el mensajito de vuelta
    message = "\n+Rendimiento MNs\n" + \
    Tabla.get_string()+ '\n'  \
    '-Total: ' + "{0:.{1}f}".format(Total_Coins_Day, cfg['COIN']['decimals']) + ' ' + cfg['COIN']['acronym'] + "{0:.{1}f}".format(Total_EUR_Day, 2) + '€\n'

    return message

def mostrar_inversores():
    #Variable para calcular el balance total
    Total_Balance = 0.0

    #Init return message
    message = ""

    #Get balance for all nodes
    my_addresses = cfg['MASTERNODES'] if ('MASTERNODES' in cfg.keys()) else [];
    for mn in my_addresses:
        # Ponemos titulo a la tabla de inversores por masternodo
        message += '\n+Inversores ' + mn['name']

        # Construimos la dichosa tablita
        Tabla = PrettyTable()
        Tabla.padding_width = 0
        Tabla.field_names = ['Nombre', '(%)', 'Mined', 'Total']

        MN_Current_Coins = get_balance(mn['address'])
        MN_Generated     = MN_Current_Coins - float(mn['setup_balance'])

        # Get inverstors for current masternode
        my_investors = mn['INVESTORS'] if ('INVESTORS' in mn.keys()) else [];

        #Loop through all investors for current MN
        for inv in my_investors:
            inv_percent   = (float(inv['coins'])/float(cfg['COIN']['collateral']))*100.0
            inv_generated = float(MN_Generated)*(inv_percent/100.0)
            inv_total     = float(inv['coins']) + inv_generated
            Tabla.add_row([inv['name'], "{0:.{1}f}".format(inv_percent, 2), "{0:.{1}f}".format(inv_generated, cfg['COIN']['decimals']), "{0:.{1}f}".format(inv_total, cfg['COIN']['decimals'])])

        message += '\n' + Tabla.get_string() + '\n' '-Total mined: ' + "{0:.{1}f}".format(MN_Generated, cfg['COIN']['decimals']) + ' ' + cfg['COIN']['acronym'] + '\n'

    return message

def comando_bot(cmd):
    if   (cmd == "AYUDA"):
        message = mostrar_ayuda()
    elif (cmd == "PRECIO"):
        message = mostrar_precio()
    elif (cmd == "BALANCE"):
        message = mostrar_balance()
    elif (cmd == "INVERSORES"):
        message = mostrar_inversores()
    elif (cmd == "RENDIMIENTO"):
        message =  mostrar_rendimiento()
    else:
        message = "\n-Error! Comando desconocido.\nTeclee '/bot ayuda' para mostrar una lista de los comandos disponibles."

    return message

@client.event
async def on_ready():
    print(cfg['COIN']['name'] + " BOT funcionando")

@client.event
async def on_message(message):
    if (message.content.upper()[0:5]=="/BOT "):
        return_message = comando_bot(message.content.upper()[5:])
        await client.send_message(message.channel, "```diff" + return_message + "\n```")

client.run(cfg['DISCORD']['api_key'])
