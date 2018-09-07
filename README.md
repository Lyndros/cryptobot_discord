<html>
<body style="font-family: Consolas, monospace; font-size:14pt;">
<br/> <b>Discord BOT Installation instructions</b>
<br/> ─────────────────────────────────────────────────────────────────────────────────
<br/>
<br/> A beautiful discord bot that allows you to track your favourite masternodes balances and performances.
<br/>
<br/> <b>0. Requirements</b>
<br/>
<br/> In order to run this program the following python3 and the following libraries need to be installed:
<br/> &nbsp; &nbsp; $sudo apt-get install python3-pip python3-yaml
<br/> &nbsp; &nbsp; $sudo pip install -U discord.py
<br/> &nbsp; &nbsp; $sudo pip install coinmarketcap
<br/> &nbsp; &nbsp; $sudo pip install PrettyTable
<br/>
<br/> <b>1. Copying the necessary files</b>
<br/>
<br/> &nbsp; &nbsp; $mkdir -p /opt/discord_bots/
<br/> &nbsp; &nbsp; $cd /opt/discord_bots/
<br/> &nbsp; &nbsp; $wget https://raw.githubusercontent.com/Lyndros/crypto_tools/master/discord_bots/discord_superbot.py
<br/>
<br/> -- These are configuration examples, you need to customize them --
<br/> &nbsp; &nbsp; $wget https://raw.githubusercontent.com/Lyndros/crypto_tools/master/discord_bots/config_smartcash.yml
<br/> &nbsp; &nbsp; $wget https://raw.githubusercontent.com/Lyndros/crypto_tools/master/discord_bots/config_tokugawa.yml
<br/>
<br/> <b>2. Setting your configuration file</b>
<br/> 
<br/> Edit the configuration file and modify as needed; coin parameters, masternodes addresses, etc...
<br/> If the coin explorer base url is not known by you contact the coin developer.
<br/> In the Discord section add your API key (check how to create a key <a href="https://discordpy.readthedocs.io/en/rewrite/discord.html">here</a>).
<br/>
<br/> <b>3. Executing the script</b>
<br/> &nbsp; &nbsp; $python3 discord_bot.py your_configuration.yml &
<br/>
<br/> <b>4. Optional starting the bot automatically at boot</b>
<br/> Copy the <a href="https://github.com/Lyndros/crypto_tools/blob/master/services/discord_bots">discord_bots.sh</a> to /etc/init.d/. 
<br/> &nbsp; &nbsp; $systemctl enable discord_bots
<br/>
<br/> <b>5. Chatting withs your bot</b>
<br/> To see a list of available bot commands, open a chat with your bot and type "/bot ayuda"
<br/>
<br/> <b>6. Donations</b>
<br/> If you want o support this repository I accept donations even 1 TOK is always welcome :-)!
<br/> &nbsp; &nbsp;> <b>ethereum address:</b> <i>0x44F102616C8e19fF3FED10c0b05B3d23595211ce</i>
<br/> &nbsp; &nbsp;> <b>tokugawa address:</b> <i>TjrQBaaCPoVW9mPAZHPfVx9JJCq7yZ7QnA</i>
<br/>
<br/> For any questions feel free to contact me at <i>lyndros@hotmail.com</i>
</body>
</html>