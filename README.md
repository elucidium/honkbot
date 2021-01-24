# HonkBot

A bot written for 15-122's Discord server (started in Spring 2021).

## Quickstart

### Setting up the repository
- Make sure that Python 3 and `pip` are installed and up-to-date (refer to platform-appropriate resources for more information).
- Fork this repository, clone it locally, and run `pip install -r requirements.txt` in the repository directory. This will install the libraries need to work with the Discord API and Heroku Redis.

### Setting up in Discord Developer Portal
- Log into a Discord account through the [Discord Developer Portal](https://discord.com/developers/applications) and create a "New Application" with whatever metadata you want (bot name, profile picture, description).
- Go to the "Bot" tab in the left sidebar and click "Add Bot", then confirm the action.
- Scroll down in the resulting options, then **uncheck "Public Bot"** (so that the bot can't be added by others), **check "Server Members Intent"** (so that the bot can manage roles of students), and **check "Administrator" under "Bot Permissions"**.
- Go to the OAuth tab in the left sidebar, scroll down, and select the "bot" option. Once this has been done, a copyable link will show up---this is the link you will use to invite the bot to your server(s).

### Setting up on Heroku

(Note: you will probably want to have a Heroku account with a verified payment method in order to have 1000 free dyno hours per month, letting you run your bot without worrying about exceeding the base limit of 550 hours.)

- Log into [Heroku](https://www.heroku.com/) and create a new app.
- Go to the "Resources" tab and add the add-on Heroku Redis.
- Head over to the "Deploy" tab and connect the Heroku app to your forked repository.

### Pulling necessary credentials

You will need two pieces of information: a Discord authorization token and a Redis authorization token.

- For Discord, under the "Bot" tab, select "Click to Reveal Token".
- For Heroku Redis, go to the "Resources" tab, click on "Heroku Redis" in the list of add-ons, then go to the "Settings" tab and hit "View Credentials". The information you will want is the URI.
- **Locally,** make a file named `.env` in the root directory of your cloned repository, add the tokens using the following format, and save the file.
```
DISCORD_TOKEN=XXXXXXXX...
REDIS_TOKEN=redis://:XXXXXXXX...
```
- **On Heroku,** go to the "Settings" tab, scroll down and "Reveal Config Vars", then add the above tokens.

### Testing locally
Once all the above setup has been done, you can test your bot locally by running `python HonkBot.py` in the terminal.

### Deploying on Heroku
Go to the "Deploy" tab, scroll all the way down, and select "Deploy Branch".
