<html>
<body style="font-family: Consolas, monospace; font-size:14pt;">
<br/> Discord BOT Installation instructions
<br/> ─────────────────────────────────────
<br/> A beautiful discord bot that allows you to track your masternode balance and performance.
<br/>
<br/> Just copy the script discord_bot.py and the relevant configuration file to the desire installation directory;
<br/>
<br/> &nbsp; &nbsp; $mkdir -p /opt/discord_bots/
<br/> &nbsp; &nbsp; $cd /opt/discord_bots/
<br/> &nbsp; &nbsp; $wget https://raw.githubusercontent.com/Lyndros/crypto_tools/master/discord_bots/discord_superbot.py
<br/>
<br/> -- These are configuration examples, you need to customize them --
<br/> &nbsp; &nbsp; $wget https://raw.githubusercontent.com/Lyndros/crypto_tools/master/discord_bots/config_smartcash.yml
<br/> &nbsp; &nbsp; $wget https://raw.githubusercontent.com/Lyndros/crypto_tools/master/discord_bots/config_tokugawa.yml
<br/>
<br/> Edit the configuration file and modify as needed; coin parameters, masternodes addresses, etc...
<br/> If the coin explorer base url is not known by you contact the coin developer.
<br/> In the Discord section add your API key (check how to create a key <a href="https://discordpy.readthedocs.io/en/rewrite/discord.html">here</a>).
<br/>
<br/> Once your configuration file is finished launch the script:
<br/> $python3 discord_bot.py your_configuration.yml &
<br/>
<br/> To start the bot automatically at boot:
<br/> &nbsp; &nbsp; Copy the <a href="https://github.com/Lyndros/crypto_tools/blob/master/services/discord_bots">discord_bots.sh</a> to /etc/init.d/. 
<br/> &nbsp; $systemctl enable discord_bots
<br/>
<br/> If you want o support this repository I accept donations even 1 TOK is always welcome :-)!
<br/> &nbsp; &nbsp;> <b>ethereum address:</b> <i>0x44F102616C8e19fF3FED10c0b05B3d23595211ce</i>
<br/> &nbsp; &nbsp;> <b>tokugawa address:</b> <i>TjrQBaaCPoVW9mPAZHPfVx9JJCq7yZ7QnA</i>
<br/>
<br/> For any questions feel free to contact me at lyndros@hotmail.com
</body>
</html>