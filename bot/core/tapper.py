import aiohttp
import asyncio
import fasteners
import json
import os
import random
from urllib.parse import unquote

import pytz
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from datetime import datetime, timezone

from telethon import TelegramClient
from telethon.errors import *
from telethon.types import InputUser, InputBotAppShortName, InputPeerUser
from telethon.functions import messages, contacts

from .agents import generate_random_user_agent
from bot.config import settings
from bot.utils import logger, log_error, proxy_utils, config_utils, CONFIG_PATH, SESSIONS_PATH
from bot.exceptions import InvalidSession
from .headers import headers, get_sec_ch_ua


class Tapper:
    def __init__(self, tg_client: TelegramClient):
        self.tg_client = tg_client
        self.session_name, _ = os.path.splitext(os.path.basename(tg_client.session.filename))
        self.config = config_utils.get_session_config(self.session_name, CONFIG_PATH)
        self.proxy = self.config.get('proxy', None)
        self.lock = fasteners.InterProcessLock(os.path.join(SESSIONS_PATH, f"{self.session_name}.lock"))
        self.headers = headers
        self.headers['User-Agent'] = self.check_user_agent()
        self.headers.update(**get_sec_ch_ua(self.headers.get('User-Agent', '')))

    def check_user_agent(self):
        user_agent = self.config.get('user_agent')
        if not user_agent:
            user_agent = generate_random_user_agent()
            self.config['user_agent'] = user_agent
            config_utils.update_session_config_in_file(self.session_name, self.config, CONFIG_PATH)

        return user_agent

    def log_message(self, message) -> str:
        return f"<light-yellow>{self.session_name}</light-yellow> | {message}"

    async def get_tg_web_data(self) -> str | None:

        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            proxy_dict = proxy_utils.to_telethon_proxy(proxy)
        else:
            proxy_dict = None

        self.tg_client.set_proxy(proxy_dict)

        tg_web_data = None
        with self.lock:
            async with self.tg_client as client:
                while True:
                    try:
                        resolve_result = await client(contacts.ResolveUsernameRequest(username='DiamoreCryptoBot'))
                        peer = InputPeerUser(user_id=resolve_result.peer.user_id,
                                             access_hash=resolve_result.users[0].access_hash)
                        break
                    except FloodWaitError as fl:
                        fls = fl.seconds

                        logger.warning(self.log_message(f"FloodWait {fl}"))
                        logger.info(self.log_message(f"Sleep {fls}s"))
                        await asyncio.sleep(fls + 3)

                start_param = settings.REF_ID if random.randint(0, 100) <= 85 else "525256526"

                input_user = InputUser(user_id=resolve_result.peer.user_id,
                                       access_hash=resolve_result.users[0].access_hash)
                input_bot_app = InputBotAppShortName(bot_id=input_user, short_name="app")

                web_view = await self.tg_client(messages.RequestAppWebViewRequest(
                    peer=peer,
                    app=input_bot_app,
                    platform='android',
                    write_allowed=True,
                    start_param=start_param
                ))

                auth_url = web_view.url
                tg_web_data = unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

        return tg_web_data

    async def user(self, http_client: aiohttp.ClientSession):
        try:
            await http_client.post(url='https://api.diamore.co/user/visit')
            response = await http_client.get(url='https://api.diamore.co/user')
            response.raise_for_status()
            response_text = await response.text()
            app_user_data = json.loads(response_text)
            return app_user_data
        except Exception as error:
            log_error(self.log_message(f"Auth request error happened: {error}"))
            return None

    async def claim_daily(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.post(url='https://api.diamore.co/daily/claim')
            if response.status in [200, 201]:
                return True
            return False
        except Exception as error:
            log_error(self.log_message(f"Daily claim error happened: {error}"))
            return None

    async def get_quests(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(url='https://api.diamore.co/quests')
            response_text = await response.text()
            data = json.loads(response_text)
            quests_with_timer = []
            for quest in data:
                if quest.get('checkType') == 'timer':
                    quests_with_timer.append(quest['name'])
            return quests_with_timer

        except Exception as error:
            log_error(self.log_message(f"Get quests error happened: {error}"))
            return None

    async def finish_quests(self, http_client: aiohttp.ClientSession, quest_name: str):
        try:
            response = await http_client.post(url='https://api.diamore.co/quests/finish',
                                              json={"questName": f'{quest_name}'})
            response_text = await response.text()
            data = json.loads(response_text)
            if data.get('message') == 'Quest marked as finished':
                return True

        except Exception as error:
            log_error(self.log_message(f"Finish quests error happened: {error}"))
            return None

    async def sync_clicks(self, http_client: aiohttp.ClientSession):
        try:
            random_clicks = random.randint(settings.CLICKS[0], settings.CLICKS[1])
            response = await http_client.post(url='https://api.diamore.co/taps/claim',
                                              json={"amount": str(random_clicks)})
            response_text = await response.text()
            data = json.loads(response_text)
            if data.get('message') == 'Taps claimed':
                return (True,
                        random_clicks)

        except Exception as error:
            log_error(self.log_message(f"Sync clicks error happened: {error}"))
            return None

    async def get_ads_limit(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(url='https://api.diamore.co/ads')
            resp_json = await response.json()
            return resp_json.get('available')
        except Exception as error:
            log_error(self.log_message(f"Get ads limit error happened: {error}"))
            return 0

    async def get_upgrades(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(url='https://api.diamore.co/upgrades')
            resp_json = await response.json()
            current_tap_power = resp_json['tapPower'][0]
            future_tap_power = resp_json['tapPower'][1]

            current_tap_duration = resp_json['tapDuration'][0]
            future_tap_duration = resp_json['tapDuration'][1]

            current_tap_cooldown = resp_json['tapCoolDown'][0]
            future_tap_cooldown = resp_json['tapCoolDown'][1]
            return (current_tap_power, future_tap_power, current_tap_duration, future_tap_duration,
                    current_tap_cooldown, future_tap_cooldown)
        except Exception as error:
            log_error(self.log_message(f"Get upgrades error happened: {error}"))
            return None

    async def do_upgrade(self, http_client: aiohttp.ClientSession, type: str):
        try:
            response = await http_client.post(url='https://api.diamore.co/upgrades/buy', json={"type": type})
            resp_json = await response.json()
            if resp_json.get('message') == 'Your level has been raised!':
                return True
            else:
                return False
        except Exception as error:
            log_error(self.log_message(f"Do upgrade error happened: {error}"))
            return False

    async def watch_ad(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.post(url='https://api.diamore.co/ads/watch', json={"type": "adsgram"})
            resp_json = await response.json()
            if resp_json.get('message') == 'Ad bonus applied!':
                return True
        except Exception as error:
            log_error(self.log_message(f"Watch ads error happened: {error}"))
            return None

    async def get_rewards(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(url='https://api.diamore.co/daily/rewards')
            resp_json = await response.json()
            return resp_json
        except Exception as error:
            log_error(self.log_message(f'Get rewards error happened: {error}'))

    async def upgrade_to_level(self, http_client, upgrade_type, setting_key, level_key, log_message):
        while True:
            (current_tapPower, future_tapPower,
             current_tapDuration, future_tapDuration,
             current_tapCoolDown, future_tapCoolDown) = await self.get_upgrades(http_client)

            user = await self.user(http_client=http_client)
            if user is None:
                continue

            balance = int(float(user["balance"]))
            upgrade_info = locals()[f"future_{upgrade_type}"]
            level = upgrade_info.get('level')
            price = int(float(upgrade_info.get('price')))

            if level >= getattr(settings, setting_key):
                break
            else:
                if balance > price:
                    status = await self.do_upgrade(http_client=http_client, type=upgrade_type)
                    if status:
                        logger.success(self.log_message(f'Successfully upgraded {log_message}, level - {level + 1}, '
                                                        f'balance - {balance - price}'))
                    else:
                        logger.warning(
                            self.log_message(f'Something wrong in upgrade. Balance: {balance}. Upgrade price: {price}'))
                        break
                else:
                    logger.info(self.log_message(f'Not enough money to upgrade {log_message}'))
                    break

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: str) -> bool:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(self.log_message(f"Proxy IP: {ip}"))
            return True
        except Exception as error:
            log_error(self.log_message(f"Proxy: {proxy} | Error: {error}"))
            return False

    async def run(self) -> None:
        random_delay = random.randint(1, settings.RANDOM_DELAY_IN_RUN)
        logger.info(self.log_message(f"Bot will start in <ly>{random_delay}s</ly>"))
        await asyncio.sleep(random_delay)

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

        init_data = await self.get_tg_web_data()

        if not init_data:
            if not http_client.closed:
                await http_client.close()
            if proxy_conn and not proxy_conn.closed:
                proxy_conn.close()
            return

        http_client.headers['Authorization'] = f'Token {init_data}'

        while True:
            try:
                user = await self.user(http_client=http_client)
                if user is None:
                    continue

                logger.info(self.log_message(f'Balance - {int(float(user["balance"]))}'))

                await asyncio.sleep(1.5)

                rewards = await self.get_rewards(http_client)
                if rewards.get('current') != "0":
                    claim_daily = await self.claim_daily(http_client=http_client)
                    if claim_daily:
                        logger.info(self.log_message('Claimed daily'))
                else:
                    logger.info(self.log_message('Daily bonus not available'))

                await asyncio.sleep(1.5)

                if not user['quests']:
                    quests = await self.get_quests(http_client=http_client)
                    for quest_name in quests:
                        status = await self.finish_quests(http_client=http_client, quest_name=quest_name)
                        if status is True:
                            logger.info(self.log_message(f'Successfully done {quest_name} quest'))
                elif user['quests']:
                    quests = await self.get_quests(http_client=http_client)
                    completed_quests = []
                    new_quests = []
                    for quest in user['quests']:
                        if quest['status'] == 'completed':
                            completed_quests.append(quest['name'])
                    for quest_name in quests:
                        if quest_name not in completed_quests:
                            new_quests.append(quest_name)
                    for quest_name in new_quests:
                        status = await self.finish_quests(http_client=http_client, quest_name=quest_name)
                        if status is True:
                            logger.info(self.log_message(f'Successfully done {quest_name} quest'))

                await asyncio.sleep(1.5)
                next_tap_delay = None
                limit_date_str = user.get("limitDate")
                if limit_date_str or limit_date_str is None:
                    if limit_date_str:
                        limit_date = datetime.fromisoformat(limit_date_str.replace("Z", "+00:00"))
                    else:
                        limit_date = datetime.min.replace(tzinfo=timezone.utc)

                    current_time_utc = datetime.now(pytz.utc)

                    if current_time_utc > limit_date:
                        status, clicks = await self.sync_clicks(http_client=http_client)
                        if status is True:
                            user = await self.user(http_client=http_client)
                            logger.success(self.log_message(f'Played game, got - {clicks} diamonds, '
                                                            f'balance - {int(float(user["balance"]))}'))
                    else:
                        logger.info(self.log_message('Game on cooldown'))
                        next_tap_delay = limit_date - current_time_utc

                await asyncio.sleep(1.5)

                ads_count = await self.get_ads_limit(http_client)
                if ads_count:
                    while ads_count > 0:
                        status = await self.watch_ad(http_client)
                        if status:
                            logger.success(self.log_message(f'Watched ad to skip game cooldown'))
                            status, clicks = await self.sync_clicks(http_client=http_client)
                            user = await self.user(http_client=http_client)
                            logger.success(self.log_message(
                                f'Played game, got - {clicks} diamonds, balance - {int(float(user["balance"]))}'))
                        ads_count -= 1

                if settings.AUTO_UPGRADE_REDUCE_COOLDOWN:
                    await self.upgrade_to_level(http_client, "tapCoolDown", "AUTO_UPGRADE_REDUCE_COOLDOWN_LEVEL",
                                                "game cooldown", "game cooldown")

                if settings.AUTO_UPGRADE_CLICKING_POWER:
                    await self.upgrade_to_level(http_client, "tapPower", "AUTO_UPGRADE_CLICKING_POWER_LEVEL",
                                                "game tap power", "game tap power")

                if settings.AUTO_UPGRADE_TIMER:
                    await self.upgrade_to_level(http_client, "tapDuration", "AUTO_UPGRADE_TIMER_LEVEL",
                                                "game duration", "game duration")

                if next_tap_delay is None or next_tap_delay.seconds > 3600:
                    sleep_time = random.randint(3500, 3600)
                else:
                    sleep_time = next_tap_delay.seconds

                logger.info(self.log_message(f'Sleep {round(sleep_time / 60, 2)} min'))
                await asyncio.sleep(sleep_time)

            except InvalidSession as error:
                raise error

            except Exception as error:
                log_error(self.log_message(f"Unknown error: {error}"))
                await asyncio.sleep(delay=3)


async def run_tapper(tg_client: TelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
    finally:
        if runner.lock.acquired:
            runner.lock.release()
