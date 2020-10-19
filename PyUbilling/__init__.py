import asyncio
import datetime
import json
import xml.etree.ElementTree as xml
from typing import List, Optional, Union
from urllib.parse import urlparse, urlunparse

from loguru import logger
from sys import stdout

import aiohttp

from .structures import (user_announcement, user_paument_systems, user_payment,
                         user_tickets, user_w_auto)

class BillClass():

    def __init__(self, api_link,
                 loop: Optional[Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop]] = None):

        logger.add(stdout, colorize=True, format="<green>{time:DD.MM.YY H:mm:ss}</green> "
                "| <yellow><b>{level}</b></yellow> | <magenta>{file}</magenta> | <cyan>{message}</cyan>")

        if api_link:
            self._main_loop = loop
            self.o = urlparse(api_link)

            if self.o.scheme == '':
                raise ValueError(f'Url must contain http, not: {api_link}')

            self._session: Optional[aiohttp.ClientSession] = None

        else:
            raise ValueError('api_link should not be NONE')

    def get_new_session(self):
        return aiohttp.ClientSession(loop=self.loop())

    def loop(self):
        return self._main_loop

    def session(self):
        if self._session is None or self._session.closed:
            self._session = self.get_new_session()
        return self._session

    async def close(self):
        await self._session.close()

    async def get_response(self, query):
        loc_session = self.session()
        link = urlunparse(self.o._replace(query=query))

        async with loc_session.get(link) as resp:

            if resp.status != 200:
                msg = f"The server returned HTTP {resp.status} {resp.reason}. Response body:\n[{await resp.text()}]"
                await self.close()
                raise RuntimeError(msg)

            logger.success(link) # я просто ссылку логирую
            answer = await resp.read()

        await self.close()
        return answer

    async def get_user_w_auto(self, user) -> user_w_auto:

        if user.login and user.password:

            query = f'xmlagent=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
            answer = await self.get_response(query)

            try:
                answer = user_w_auto(json.loads(answer))

            except json.decoder.JSONDecodeError:
                answer = xml.fromstring(answer)

                tmp_dict = {}

                for table in answer.iter('userdata'):
                    for row in table:
                        tmp_dict[row.tag] = row.text

                answer = user_w_auto(tmp_dict)

            if answer == {}: answer = None
            return answer

        else:
            raise ValueError('Login and password should not be NONE')

    async def get_user_payment(self, user) -> List[user_payment]:

        if user.login and user.password:

            s: List[user_payment] = []

            query = f'xmlagent=true&payments=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
            #query = 'xmlagent=true&payments=true&json=true'   # debug 
            answer = await self.get_response(query)

            try:
                answer = json.loads(answer)
            except json.decoder.JSONDecodeError:
                answer = xml.fromstring(answer)

                tmp_ans = []

                for table in answer.iter('payment'):
                    temp_dict = {}
                    for row in table:
                        temp_dict[row.tag] = row.text
                    tmp_ans.append(temp_dict)
                answer = tmp_ans

            for row in answer:
                row['date'] = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
                s.append(user_payment(row))

            if s == []: s = None
            return s

        else:
            raise ValueError('Login and password should not be NONE')

    async def get_user_announcement(self, user) -> List[user_payment]:

        if user.login and user.password:

            s: List[user_payment] = []

            query = f'xmlagent=true&announcements=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
            answer = await self.get_response(query)

            try:
                answer = json.loads(answer)
                for row in answer:
                    s.append(user_announcement(row))

            except json.decoder.JSONDecodeError:
                answer = xml.fromstring(answer)

                for table in answer.iter('data'):
                    temp_dict = {}
                    for row in table:
                        temp_dict[row.tag] = row.text
                        temp_dict['unic'] = row.attrib['unic']
                        temp_dict['title'] = row.attrib['title']
                    s.append(user_announcement(temp_dict))

            if s == []: s = None
            return s

        else:
            raise ValueError('Login and password should not be NONE')

    async def get_user_tickets(self, user) -> List[user_tickets]:

        if user.login and user.password:

            s: List[user_tickets] = []

            query = f'xmlagent=true&tickets=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
            #query = 'xmlagent=true&tickets=true&json=true'  # debug

            answer = await self.get_response(query)

            try:
                answer = json.loads(answer)

            except json.decoder.JSONDecodeError:
                answer = xml.fromstring(answer)
                temp_ans = []

                for table in answer.iter('ticket'):
                    temp_dict = {}
                    for row in table:
                        temp_dict[row.tag] = row.text
                    temp_ans.append(user_tickets(temp_dict))
                answer = temp_ans

            for row in answer:
                row['date'] = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
                s.append(user_payment(row))

            if s == []: s = None
            return s

        else:
            raise ValueError('Login and password should not be NONE')

    async def get_user_paument_systems(self, user) -> List[user_tickets]:

        if user.login and user.password:

            s: List[user_tickets] = []

            query = f'xmlagent=true&opayz=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
            answer = await self.get_response(query)

            try:
                answer = json.loads(answer)
            except json.decoder.JSONDecodeError:
                answer = xml.fromstring(answer)
                tmp_ans = []

                for table in answer.iter('paysys'):
                    tmp_dict = {}
                    for row in table:
                        tmp_dict[row.tag] = row.text
                    tmp_ans.append(tmp_dict)
                answer = tmp_ans

            for row in answer:
                s.append(user_paument_systems(row))

            if s == []: s = None
            return s

        else:
            raise ValueError('Login and password should not be NONE')
