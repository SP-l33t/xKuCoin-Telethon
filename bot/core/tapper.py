import aiohttp
import asyncio
import base64
import fasteners
import os
import random
import time
from urllib.parse import unquote
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from time import time

from telethon import TelegramClient
from telethon.errors import *
from telethon.types import InputUser, InputBotAppShortName, InputPeerUser
from telethon.functions import messages, contacts

from .agents import generate_random_user_agent
from bot.config import settings
from bot.utils import logger, log_error, proxy_utils, config_utils, CONFIG_PATH, SESSIONS_PATH
from bot.exceptions import InvalidSession
from .headers import headers, get_sec_ch_ua


XKUCOIN_API = "https://www.kucoin.com/_api/xkucoin"


class Tapper:
    def __init__(self, tg_client: TelegramClient):
        self.tg_client = tg_client
        self.session_name, _ = os.path.splitext(os.path.basename(tg_client.session.filename))
        self.config = config_utils.get_session_config(self.session_name, CONFIG_PATH)
        self.proxy = self.config.get('proxy', None)
        self.lock = fasteners.InterProcessLock(os.path.join(SESSIONS_PATH, f"{self.session_name}.lock"))
        self.start_param = ''
        self.headers = headers
        self.headers['User-Agent'] = self.check_user_agent()
        self.headers.update(**get_sec_ch_ua(self.headers.get('User-Agent', '')))

    def log_message(self, message) -> str:
        return f"<light-yellow>{self.session_name}</light-yellow> | {message}"

    def check_user_agent(self):
        user_agent = self.config.get('user_agent')
        if not user_agent:
            user_agent = generate_random_user_agent()
            self.config['user_agent'] = user_agent
            config_utils.update_session_config_in_file(self.session_name, self.config, CONFIG_PATH)

        return user_agent

    async def get_tg_web_data(self) -> dict[str, str]:
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            proxy_dict = proxy_utils.to_telethon_proxy(proxy)
        else:
            proxy_dict = None
        self.tg_client.set_proxy(proxy_dict)

        init_data = {}
        with self.lock:
            async with self.tg_client as client:
                while True:
                    try:
                        resolve_result = await client(contacts.ResolveUsernameRequest(username='xkucoinbot'))
                        peer = InputPeerUser(user_id=resolve_result.peer.user_id,
                                             access_hash=resolve_result.users[0].access_hash)
                        break
                    except FloodWaitError as fl:
                        fls = fl.seconds

                        logger.warning(self.log_message(f"FloodWait {fl}"))
                        logger.info(self.log_message(f"Sleep {fls}s"))
                        await asyncio.sleep(fls + 3)

                ref_id = settings.REF_ID if random.randint(0, 100) <= 85 \
                    else "cm91dGU9JTJGdGFwLWdhbWUlM0ZpbnZpdGVyVXNlcklkJTNENTI1MjU2NTI2JTI2cmNvZGUlM0Q="

                input_user = InputUser(user_id=resolve_result.peer.user_id,
                                       access_hash=resolve_result.users[0].access_hash)
                input_bot_app = InputBotAppShortName(bot_id=input_user, short_name="kucoinminiapp")

                web_view = await client(messages.RequestAppWebViewRequest(
                    peer=peer,
                    app=input_bot_app,
                    platform='android',
                    write_allowed=True,
                    start_param=ref_id
                ))

                auth_url = web_view.url
                init_data = {}
                tg_web_data = unquote(
                    string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))

                user_data = re.findall(r'user=([^&]+)', tg_web_data)[0]
                chat_instance = re.findall(r'chat_instance=([^&]+)', tg_web_data)[0]
                chat_type = re.findall(r'chat_type=([^&]+)', tg_web_data)[0]
                start_param = re.findall(r'start_param=([^&]+)', tg_web_data)[0]
                auth_date = re.findall(r'auth_date=([^&]+)', tg_web_data)[0]
                hash_value = re.findall(r'hash=([^&]+)', tg_web_data)[0]
                self.start_param = start_param

                init_data['auth_date'] = auth_date
                init_data['chat_instance'] = chat_instance
                init_data['chat_type'] = chat_type
                init_data['hash'] = hash_value
                init_data['start_param'] = start_param
                init_data['user'] = user_data.replace('"', '\"')
                init_data['via'] = "miniApp"

        return init_data

    async def login(self, http_client: aiohttp.ClientSession, tg_web_data: dict[str, str]):
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
            await asyncio.sleep(delay=random.uniform(3, 7))

    async def get_info_data(self, http_client: aiohttp.ClientSession):
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
            await asyncio.sleep(delay=random.uniform(3, 7))

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: str) -> bool:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(15))
            ip = (await response.json()).get('origin')
            logger.info(self.log_message(f"Proxy IP: {ip}"))
            return True
        except Exception as error:
            log_error(self.log_message(f"Proxy: {proxy} | Error: {error}"))
            return False

    async def claim_init_reward(self, http_client: aiohttp.ClientSession):
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

    async def send_taps(self, http_client: aiohttp.ClientSession, taps: int, available_taps: int):
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
        random_delay = random.randint(1, settings.START_DELAY)
        logger.info(self.log_message(f"Bot will start in <ly>{random_delay}s</ly>"))
        await asyncio.sleep(random_delay)

        access_token_created_time = 0

        proxy_conn = None
        if self.proxy:
            proxy_conn = ProxyConnector().from_url(self.proxy)
            http_client = CloudflareScraper(headers=self.headers, connector=proxy_conn)
            p_type = proxy_conn._proxy_type
            p_host = proxy_conn._proxy_host
            p_port = proxy_conn._proxy_port
            if not await self.check_proxy(http_client=http_client, proxy=f"{p_type}://{p_host}:{p_port}"):
                return
        else:
            http_client = CloudflareScraper(headers=self.headers)

        token_live_time = random.randint(3500, 3600)

        while True:
            try:
                sleep_time = random.uniform(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                if time() - access_token_created_time >= token_live_time:
                    tg_web_data = await self.get_tg_web_data()

                    if not tg_web_data:
                        if not http_client.closed:
                            await http_client.close()
                        if proxy_conn and not proxy_conn.closed:
                            proxy_conn.close()
                        return

                    login_data = await self.login(http_client=http_client, tg_web_data=tg_web_data)
                    if not login_data.get('success', False):
                        logger.warning(self.log_message(f'Error while loging in: {login_data.get("msg")}'))
                        continue

                    access_token_created_time = time()
                    token_live_time = random.randint(3500, 3600)
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
                        sleep_before_taps = int((taps_limit - available_taps) / recover_speed)
                        logger.info(self.log_message(f'Not enough taps, going to sleep '
                                                     f'<y>{round(sleep_before_taps / 60, 1)}</y> min'))
                        await asyncio.sleep(delay=sleep_before_taps)
                        available_taps = taps_limit

                    while available_taps > settings.MIN_ENERGY:
                        taps = min(available_taps, random.randint(settings.RANDOM_TAPS_COUNT[0], settings.RANDOM_TAPS_COUNT[1]))
                        response = await self.send_taps(http_client=http_client, taps=taps, available_taps=available_taps)
                        if response:
                            await asyncio.sleep(delay=interval)
                            available_taps = available_taps - taps + (interval * recover_speed)
                            logger.success(self.log_message(f"Successful tapped! Got <g>+{taps}</g> Coins | "
                                                            f"Available Taps:<lc>{available_taps}</lc>"))
                        else:
                            logger.warning(self.log_message(f"Failed send taps"))
                            break

                logger.info(self.log_message(f"Sleep <y>{round(sleep_time / 60, 1)}</y> min"))
                await asyncio.sleep(delay=sleep_time)

            except InvalidSession as error:
                raise error

            except Exception as error:
                log_error(self.log_message(f"Unknown error: {error}"))
                await asyncio.sleep(delay=random.uniform(60, 120))


async def run_tapper(tg_client: TelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
    finally:
        if runner.lock.acquired:
            runner.lock.release()
