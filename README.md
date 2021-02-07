# Calendar Bot
A simple bot to view and use a calendar in discord. This is a work in progress!
# Installation
**1.** Python 3.9 and PostgreSQL is required to run this bot installation [here](https://www.python.org/) and [here](https://www.postgresql.org/)
**2.** Get the code and install the requirements
```sh
git clone https://github.com/pikaninja/Calendar.git
```
Then navigate to the directory created and install the requirements
```sh
pip install -U requirements.txt
```
**3.** Set up PostgreSQL
Inside the postgres command prompt, `psql`, tupe
```sql
CREATE ROLE calendarbot WITH LOGIN PASSWORD 'password';
CREATE DATABASE calendar OWNER calendarbot;
```
**4.** Creating the config file
First copy the sample config file into a new file, `config.toml`
```toml
TOKEN = "token" # Your bot's token
PREFIX = "cb/" # Default prefix is "cb/", you can change it if you want
OWNER_IDS = [1, 2, 3] # Put your id and others for the ones who will get powers in the bot

[database]
# all options defined here are passed to asyncpg.create_pool
host = "localhost" # Most likely localhost unless you're hosting elsewhere, in which case you should know what you're doing
database = "calendar" # We created the database earlier
password = "password" # The password you used
user = "calendarbot" # Also created above

[jishaku]
# optional - all flags defined here are set by the bot
JISHAKU_NO_UNDERSCORE = true
JISHAKU_NO_DM_TRACEBACK = true```
**5.** Running the bot
To run our bot now, all we have to do is
```sh
python3.9 main.py
```
Which will start up our bot!
