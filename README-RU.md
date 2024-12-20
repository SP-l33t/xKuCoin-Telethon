[![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/xkucoinbot/kucoinminiapp?startapp=cm91dGU9JTJGdGFwLWdhbWUlM0ZpbnZpdGVyVXNlcklkJTNENTI1MjU2NTI2JTI2cmNvZGUlM0Q=)

## Рекомендация перед использованием

# 🔥🔥 Используйте PYTHON 3.10 🔥🔥

> 🇪🇳 README in english available [here](README.md)

## Функционал  
|               Функционал               | Поддерживается |
|:--------------------------------------:|:--------------:|
|            Многопоточность             |       ✅        |
|        Привязка прокси к сессии        |       ✅        |
|      Привязка User-Agent к сессии      |       ✅        |
|         Авторегистрация в боте         |       ✅        |
|               Авто-тапы                |       ✅        |
| Поддержка telethon И pyrogram .session |       ✅        |

_Скрипт осуществляет поиск файлов сессий в следующих папках:_
* /sessions
* /sessions/pyrogram
* /session/telethon



## [Настройки](https://github.com/SP-l33t/xKuCoin-Telethon/blob/master/.env-example/)
|         Настройка         |                                                                                                                              Описание                                                                                                                               |
|:-------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|   **API_ID / API_HASH**   |                                                                                                        Данные платформы, с которой запускать сессию Telegram                                                                                                        | 
|  **GLOBAL_CONFIG_PATH**   | Определяет глобальный путь для accounts_config, proxies, sessions. <br/>Укажите абсолютный путь или используйте переменную окружения (по умолчанию - переменная окружения: **TG_FARM**)<br/> Если переменной окружения не существует, использует директорию скрипта |
|       **FIX_CERT**        |                                                                                              Попытаться исправить ошибку SSLCertVerificationError ( True / **False** )                                                                                              |
|      **SLEEP_TIME**       |                                                                                                        Время сна между циклами (по умолчанию - [3600, 4000])                                                                                                        |
|      **START_DELAY**      |                                                                        Задержка для старта каждой сессии от 1 до установленного значения (по умолчанию : **30**, задержка в интервале 1..30)                                                                        |
|   **RANDOM_TAPS_COUNT**   |                                                                                                       Количество кликов на запрос (по умолчанию - [[40, 55]]                                                                                                        |
|      **MIN_ENERGY**       |                                                                                      Минимальное количество доступной энергии, когда бот перестает тапать (по умолчанию - 10)                                                                                       |
|        **REF_ID**         |                                                                                                                 Реф. ссылка для регистрации в боте                                                                                                                  |
|  **SESSIONS_PER_PROXY**   |                                                                                           Количество сессий, которые могут использовать один прокси (По умолчанию **1** )                                                                                           |
|  **USE_PROXY_FROM_FILE**  |                                                                                             Использовать ли прокси из файла `bot/config/proxies.txt` (**True** / False)                                                                                             |
| **DISABLE_PROXY_REPLACE** |                                                                                   Отключить автоматическую проверку и замену нерабочих прокси перед стартом ( True / **False** )                                                                                    |
|     **DEVICE_PARAMS**     |                                                                                  Вводить параметры устройства, чтобы сделать сессию более похожую, на реальную  (True / **False**)                                                                                  |
|     **DEBUG_LOGGING**     |                                                                                               Включить логирование трейсбэков ошибок в папку /logs (True / **False**)                                                                                               |

## Быстрый старт 📚

Для быстрой установки и последующего запуска - запустите файл run.bat на Windows или run.sh на Линукс

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) **версии 3.10**

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/SP-l33t/xKuCoin-Telethon) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
git clone https://github.com/SP-l33t/xKuCoin-Telethon
cd xKuCoin-Telethon
```

Затем для автоматической установки введите:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/xKuCoin-Telethon >>> python3 main.py --action (1/2)
# Or
~/xKuCoin-Telethon >>> python3 main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```

# Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/xKuCoin-Telethon >>> python main.py --action (1/2)
# Или
~/xKuCoin-Telethon >>> python main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```
### Использование
При первом запуске бота создайте для него сессию с помощью команды «2». В процессе будет создана папка 'sessions', в которой хранятся все сессии, а также файл accounts.json с конфигурациями.
Если у вас уже есть сессии, просто поместите их в папку 'sessions' и запустите кликер. В процессе запуска вы сможете настроить использование прокси для каждой сессии.
Юзер-агент создается для каждого аккаунта автоматически.

Пример того, как должен выглядеть accounts.json:
```shell
[
  {
    "session_name": "name_example",
    "user_agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
    "proxy": "type://user:pass:ip:port"   # "proxy": "" - если прокси не используется
  }
]
```
