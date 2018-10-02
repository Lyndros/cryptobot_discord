# Discord CryptoBot installation instructions
A beautiful discord bot that allows you to track your favourite masternodes balances and performances.

## 1. Requirements

In order to run this program the following python3 and the following libraries need to be installed:
```
$sudo apt-get install python3-pip python3-yaml
$sudo pip3 install -U discord.py
$sudo pip3 install coinmarketcap
```
## 2. Copying the necessary files
```
$mkdir -p /opt/cryptobot_discord/
$cd /opt/cryptobot_discord/
$wget https://raw.githubusercontent.com/Lyndros/cryptobot_discord/master/cryptobot_discord.py
```
-- These are configuration examples, you need to customize them --
```
$wget https://raw.githubusercontent.com/Lyndros/cryptobot_discord/master/config/smartcash_bot.yml
$wget https://raw.githubusercontent.com/Lyndros/cryptobot_discord/master/config/tokugawa_bot.yml
$wget https://raw.githubusercontent.com/Lyndros/cryptobot_discord/master/config/loki_bot.yml
```
## 3. Setting your configuration file

Edit the configuration file and modify as needed; coin parameters, masternodes addresses, etc...
If the coin explorer base url is not known by you contact the coin developer.
In the Discord section add your API key (check how to create a key <a href="https://discordpy.readthedocs.io/en/rewrite/discord.html">here</a>).

## 4. Executing the script
``` 
$python3 cryptobot_discord.py /your_path/your_configuration.yml & 
```

## 5. Optional starting the bot automatically at boot
If you want to automatically start yours bots at boot consider to add them to systemctl.
You can check the predefine bot services available in: https://github.com/Lyndros/cryptobot_discord/tree/master/service/.
Please before enabling edit the file location as needed.

i.e: Adding tokugawa bot service,
```
$cd /etc/systemd/system/
$wget https://raw.githubusercontent.com/Lyndros/cryptobot_discord/master/service/tokugawa_bot.service
$systemctl enable tokugawa_bot.service
```
i.e: Adding smartcash bot service,
```
$cd /etc/systemd/system/
$wget https://raw.githubusercontent.com/Lyndros/cryptobot_discord/master/service/smartcash_bot.service
$systemctl enable smartcash_bot.service
```
i.e: Adding loki bot service,
```
$cd /etc/systemd/system/
$wget https://raw.githubusercontent.com/Lyndros/cryptobot_discord/master/service/loki_bot.service
$systemctl enable loki_bot.service
```

## 6. Chatting withs your bot
To see a list of available bot commands, open a chat with your bot and type "/bot ayuda"

## 7. Donations
If you want o support this repository I accept donations even 1 TOK is always welcome :-)!
> <b>ethereum address:</b> <i>0x44F102616C8e19fF3FED10c0b05B3d23595211ce</i>
> <b>tokugawa address:</b> <i>TjrQBaaCPoVW9mPAZHPfVx9JJCq7yZ7QnA</i>

For any questions feel free to contact me at <i>lyndros at hotmail.com</i>
