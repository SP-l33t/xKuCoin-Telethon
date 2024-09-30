[![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/xkucoinbot/kucoinminiapp?startapp=cm91dGU9JTJGdGFwLWdhbWUlM0ZpbnZpdGVyVXNlcklkJTNEMzQyOTUyMTE3JTI2cmNvZGUlM0RRQlNXUUZVVg==)

## Recommendation before use

# 🔥🔥 Use PYTHON 3.10 🔥🔥

> 🇷 🇺 README in russian available [here](README-RU.md)

## Features  
| Feature                       | Supported |
|-------------------------------|:---------:|
| Multithreading                |     ✅     |
| Proxy binding to session      |     ✅     |
| User-Agent binding to session |     ✅     |
| Registration in bot           |     ✅     |
| Auto-taps                     |     ✅     |
| Supports telethon .session    |     ✅     |



## [Settings](https://github.com/Desamod/xKuCoinBot/blob/master/.env-example/)
| Settings                  |                                                                                                                  Description                                                                                                                  |
|---------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| **API_ID / API_HASH**     |                                                                                  Platform data from which to run the Telegram session (by default - android)                                                                                  |
| **GLOBAL_CONFIG_PATH**    | Specifies the global path for accounts_config, proxies, sessions. <br/>Specify an absolute path or use an environment variable (default environment variable: **TG_FARM**) <br/>If no environment variable exists, uses the script directory. |
| **SLEEP_TIME**            |                                                                                             Sleep time between cycles (by default - [3600, 4000])                                                                                             |
| **START_DELAY**           |                                                                      Random seconds delay for each session to start from 1 to this value (default : **30**, means 1..30)                                                                      |
| **RANDOM_TAPS_COUNT**     |                                                                                                Taps count per request (by default - [[40, 55]]                                                                                                |
| **MIN_ENERGY**            |                                                                                 Minimum amount of available energy, when bot stops tapping (by default - 10)                                                                                  |
| **REF_ID**                |                                                                                                           Ref link for registration                                                                                                           |
| **SESSIONS_PER_PROXY**    |                                                                                            Amount of sessions, that can share same proxy ( **1** )                                                                                            |
| **USE_PROXY_FROM_FILE**   |                                                                               Whether to use a proxy from the `bot/config/proxies.txt` file (**True** / False)                                                                                |
| **DISABLE_PROXY_REPLACE** |                                                                      Disable automatic checking and replacement of non-working proxies before startup (True / **False**)                                                                      |
| **DEVICE_PARAMS**         |                                                                          Enter device settings to make the telegram session look more realistic  (True / **False**)                                                                           |
| **DEBUG_LOGGING**         |                                                                                     Whether to log error's tracebacks to /logs folder (True / **False**)                                                                                      |

## Quick Start 📚

To fast install libraries and run bot - open run.bat on Windows or run.sh on Linux

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10**

## Obtaining API Keys
1. Go to my.telegram.org and log in using your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Record the API_ID and API_HASH provided after registering your application in the .env file.

## Installation
You can download the [**repository**](https://github.com/Desamod/xKuCoinBot) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/Desamod/xKuCoinBot
cd xKuCoinBot
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/xKuCoinBot >>> python3 main.py --action (1/2)
# Or
~/xKuCoinBot >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/xKuCoinBot >>> python main.py --action (1/2)
# Or
~/xKuCoinBot >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

### Usages
When you first launch the bot, create a session for it using the 'Creates a session' command. It will create a 'sessions' folder in which all accounts will be stored, as well as a file accounts.json with configurations.
If you already have sessions, simply place them in a folder 'sessions' and run the clicker. During the startup process you will be able to configure the use of a proxy for each session.
User-Agent is created automatically for each account.

Here is an example of what accounts.json should look like:
```shell
[
  {
    "session_name": "name_example",
    "user_agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
    "proxy": "type://user:pass:ip:port"  # "proxy": "" - if you dont use proxy
  }
]
```

### Contacts

For support or questions, you can contact me

[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/desforge_crypto)



