import aiohttp
import asyncio
import base64
import json
import os
import re
import time
from urllib.parse import unquote, parse_qs
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from random import randint, uniform
from time import time

from bot.utils.universal_telegram_client import UniversalTelegramClient

from bot.config import settings
from bot.utils import logger, log_error, config_utils, CONFIG_PATH, first_run
from bot.exceptions import InvalidSession
from .headers import headers, get_sec_ch_ua


XKUCOIN_API = "https://www.kucoin.com/_api/xkucoin"


class Tapper:
    def __init__(self, tg_client: UniversalTelegramClient):
        self.tg_client = tg_client
        self.session_name = tg_client.session_name

        session_config = config_utils.get_session_config(self.session_name, CONFIG_PATH)

        if not all(key in session_config for key in ('api', 'user_agent')):
            logger.critical(self.log_message('CHECK accounts_config.json as it might be corrupted'))
            exit(-1)

        self.headers = headers
        user_agent = session_config.get('user_agent')
        self.headers['user-agent'] = user_agent
        self.headers.update(**get_sec_ch_ua(user_agent))

        self.proxy = session_config.get('proxy')
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            self.tg_client.set_proxy(proxy)

        self.start_param = ''
        self.user_data = None

        self._webview_data = None

    def log_message(self, message) -> str:
        return f"<ly>{self.session_name}</ly> | {message}"

    async def get_tg_web_data(self) -> dict[str, str]:
        webview_url = await self.tg_client.get_app_webview_url('xkucoinbot', "kucoinminiapp", "cm91dGU9JTJGdGFwLWdhbWUlM0ZpbnZpdGVyVXNlcklkJTNENTI1MjU2NTI2JTI2cmNvZGUlM0Q=")

        init_data = {}
        tg_web_data = parse_qs(unquote(webview_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
        self.user_data = json.loads(tg_web_data.get('user', [''])[0])

        self.start_param = tg_web_data.get('start_param', [''])[0] or \
                           "cm91dGU9JTJGdGFwLWdhbWUlM0Zib3RfY2xpY2slM0RvcGVubWluaWFwcA=="

        init_data['hash'] = tg_web_data.get('hash', [''])[0]
        init_data['auth_date'] = tg_web_data.get('auth_date', [''])[0]
        init_data['via'] = "miniApp"
        init_data['user'] = tg_web_data.get('user', [''])[0].replace('"', '\"')
        init_data['chat_type'] = tg_web_data.get('chat_type', [''])[0]
        init_data['chat_instance'] = tg_web_data.get('chat_instance', [''])[0]
        init_data['start_param'] = self.start_param
        init_data['signature'] = tg_web_data.get('signature', [''])[0]

        return init_data

    async def check_proxy(self, http_client: CloudflareScraper) -> bool:
        proxy_conn = http_client.connector
        if proxy_conn and not hasattr(proxy_conn, '_proxy_host'):
            logger.info(self.log_message(f"Running Proxy-less"))
            return True
        try:
            response = await http_client.get(url='https://ifconfig.me/ip', timeout=aiohttp.ClientTimeout(15))
            logger.info(self.log_message(f"Proxy IP: {await response.text()}"))
            return True
        except Exception as error:
            proxy_url = f"{proxy_conn._proxy_type}://{proxy_conn._proxy_host}:{proxy_conn._proxy_port}"
            log_error(self.log_message(f"Proxy: {proxy_url} | Error: {type(error).__name__}"))
            return False

    async def login(self, http_client: CloudflareScraper, tg_web_data: dict[str, str]):
        try:
            decoded_link = base64.b64decode(bytes(self.start_param, 'utf-8') + b'==').decode("utf-8")
            json_data = {
                'extInfo': tg_web_data,
                'inviterUserId': decoded_link.split('UserId%3D')[1].split('%')[0]
            }

            http_client.headers['Content-Type'] = 'application/json'
            response = await http_client.post(f"{XKUCOIN_API}/platform-telebot/game/login?lang=en_US",
                                              json=json_data)

            response.raise_for_status()
            http_client.cookie_jar.update_cookies(response.cookies)
            response_json = await response.json()
            return response_json

        except Exception as error:
            log_error(self.log_message(f"Unknown error during logging in: {error}"))
            await asyncio.sleep(delay=uniform(3, 7))

    async def get_info_data(self, http_client: CloudflareScraper):
        try:
            http_client.headers.pop('Content-Type')
            await http_client.get(f"{XKUCOIN_API}/ucenter/user-info?lang=en_US")
            await asyncio.sleep(delay=1)
            await http_client.get(f'{XKUCOIN_API}/currency/transfer-currencies?flat=1&currencyType=2&lang=en_US')
            await http_client.get(f'{XKUCOIN_API}/currency/rates?base=USD&targets=&lang=en_US')
            await asyncio.sleep(delay=1)
            response = await http_client.get(f"{XKUCOIN_API}/platform-telebot/game/summary?lang=en_US")
            response.raise_for_status()
            response_json = await response.json()
            if response_json.get('code') == '401':
                await asyncio.sleep(delay=3)
                return await self.get_info_data(http_client=http_client)

            return response_json['data']

        except Exception as error:
            log_error(self.log_message(f"Unknown error when getting user info data: {error}"))
            await asyncio.sleep(delay=uniform(3, 7))

    async def claim_init_reward(self, http_client: CloudflareScraper):
        try:
            response = await http_client.post(f'{XKUCOIN_API}/platform-telebot/game/obtain?taskType=FIRST_REWARD')
            response.raise_for_status()
            response_json = await response.json()
            if response_json['msg'] == 'success':
                logger.success(f"{self.session_name} | Init Reward Claimed!")

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when claiming init reward: {error}")
            await asyncio.sleep(delay=3)

    @staticmethod
    def generate_random_string(length=8):
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        random_string = ''
        for _ in range(length):
            random_index = int((len(characters) * int.from_bytes(os.urandom(1), 'big')) / 256)
            random_string += characters[random_index]
        return random_string

    async def send_taps(self, http_client: CloudflareScraper, taps: int, available_taps: int):
        try:
            hash_id = self.generate_random_string(length=16)
            boundary = f'----WebKitFormBoundary{hash_id}'
            form_data = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="increment"\r\n\r\n'
                f'{taps}\r\n'
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="molecule"\r\n\r\n'
                f'{available_taps - taps}\r\n'
                f'--{boundary}--\r\n'
            )
            http_client.headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
            response = await http_client.post(f'{XKUCOIN_API}/platform-telebot/game/gold/increase?lang=en_US',
                                              data=form_data)
            http_client.headers['Content-Type'] = 'application/json'
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            log_error(self.log_message(f"Unknown error when sending taps: {error}"))
            await asyncio.sleep(delay=3)
            return None

    async def run(self) -> None:
        random_delay = uniform(1, settings.START_DELAY)
        logger.info(self.log_message(f"Bot will start in <ly>{int(random_delay)}s</ly>"))
        await asyncio.sleep(random_delay)

        access_token_created_time = 0
        tg_web_data = None

        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with CloudflareScraper(headers=self.headers, timeout=aiohttp.ClientTimeout(60), **proxy_conn) as http_client:
            while True:
                if not await self.check_proxy(http_client=http_client):
                    logger.warning(self.log_message('Failed to connect to proxy server. Sleep 5 minutes.'))
                    await asyncio.sleep(300)
                    continue

                token_live_time = randint(3500, 3600)
                try:
                    if time() - access_token_created_time >= token_live_time:
                        tg_web_data = await self.get_tg_web_data()

                        if not tg_web_data:
                            logger.warning(self.log_message('Failed to get webview URL'))
                            await asyncio.sleep(300)
                            continue

                        login_data = await self.login(http_client=http_client, tg_web_data=tg_web_data)
                        if not login_data.get('success', False):
                            logger.warning(self.log_message(f'Error while loging in: {login_data.get("msg")}'))
                            continue
                        if self.tg_client.is_fist_run:
                            await first_run.append_recurring_session(self.session_name)

                        access_token_created_time = time()
                        user_info = await self.get_info_data(http_client=http_client)
                        balance = user_info['availableAmount']
                        logger.info(self.log_message(f"Balance: <e>{balance}</e> coins"))
                        need_to_check = user_info['needToCheck']
                        if need_to_check:
                            await self.claim_init_reward(http_client=http_client)

                        game_config = user_info['gameConfig']
                        taps_limit = game_config['feedUpperLimit']
                        recover_speed = game_config['feedRecoverSpeed']
                        interval = game_config['goldIncreaseInterval']
                        available_taps = user_info['feedPreview']['molecule']
                        if available_taps <= settings.MIN_ENERGY:
                            sleep_before_taps = int((taps_limit - available_taps) * uniform(1, 1.1) / recover_speed)
                            logger.info(self.log_message(f'Not enough taps, going to sleep '
                                                         f'<y>{round(sleep_before_taps / 60, 1)}</y> min'))
                            await asyncio.sleep(delay=sleep_before_taps)
                            available_taps = taps_limit

                        while available_taps > settings.MIN_ENERGY:
                            taps = min(available_taps, randint(settings.RANDOM_TAPS_COUNT[0],
                                                                      settings.RANDOM_TAPS_COUNT[1]))
                            response = await self.send_taps(http_client=http_client, taps=taps,
                                                            available_taps=available_taps)
                            if response:
                                await asyncio.sleep(delay=interval)
                                available_taps = available_taps - taps + (interval * recover_speed)
                                logger.success(self.log_message(f"Successful tapped! Got <g>+{taps}</g> Coins | "
                                                                f"Available Taps:<lc>{available_taps}</lc>"))
                            else:
                                logger.warning(self.log_message(f"Failed send taps"))
                                break

                    sleep_time = uniform(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                    logger.info(self.log_message(f"Sleep <y>{round(sleep_time / 60, 1)}</y> min"))
                    await asyncio.sleep(delay=sleep_time)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    log_error(self.log_message(f"Unknown error: {error}"))
                    await asyncio.sleep(delay=uniform(60, 120))


async def run_tapper(tg_client: UniversalTelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
