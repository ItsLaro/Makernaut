# Makernaut
Discord bot to assist in the <a href=https://discord.com/invite/upefiu/> Official Partnered Discord server </a> of <a href=https://upe.cs.fiu.edu/> Upsilon Pi Epsilon </a> Chapter at Florida International University. 
<p align="center">
  <img src=assets\Gui_Banner.png width="1000">
  <p align="center"> Gui, the official UPE Mascot, is the face of this bot. </p>
</p>
  
## Getting started

### Requirements 
* [Discord Developer Portal: Registered Application](https://discord.com/developers/applications) - Get Bot Account registered and note down client key on a .env file as: `BOT_KEY = <key here>`
* [Google Cloud - Sheets API](https://console.cloud.google.com/apis/) - Register Project and enable the Google Sheets API. Download the credentials to your director-- the `secret_key.json`.

<b> For the UPE Makerspace bot, the keys (intended for development) can be provided by any of the moderators behind the project. </b>

### Installing

After the repo has been cloned, to install all dependencies from your directory run: 
```
$ pip install -r requirements.txt 
```
or in your virtual environment:
```
$ conda install -r requirements.txt
```

## Contributing

Work should ideally be split throughout each cog.

### Cogs

Commands and listeners are grouped/classified inside different scripts inside the `Cogs` folder. Each script is a cog and consists of a Python class that subclasses commands.Cog. On each:

* Every command is a method marked with the commands.command() decorator.

* Every listener is a method marked with the commands.Cog.listener() decorator.

* At the end, cogs are then registered with the Bot.add_cog() call.

Check out the [Discord.py](discordpy.readthedocs.io) documentation for more.

New or extended functionality should be kept inside relevant cogs. A new cog shall be created if needed. 

### PRs

Submit a pull request once the new (or fixed) feature is complete. Please add a description of the intended functionality followed by the command-chain required to test functionality with the bot on the server. 
