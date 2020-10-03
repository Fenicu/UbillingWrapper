import aiohttp
from urllib.parse import urlparse, urlunparse
from typing import Optional, Union, List
import datetime
import asyncio
import json
import xml.etree.ElementTree as xml

from structures import user_w_auto, user_payment, \
    user_announcement, user_tickets, user_paument_systems


'''
TO DO
1. XML Agent оключен конфигурацией
2. Вместо JSON возвращать кастомный словарик
3. Если ответ пустой, вернуть None
4. Убрать try\catch (альтернативно другие рейзить)
5. Для каждого вывода отдельный тип
6. s:List[Custom1] return s
7. Даты в datetime

8. Сделать функцию для запросов
9. проверять статус код

'''

class BillClass():

    #Уточнить как приходит ссылка (с http или без)
    def __init__(self, api_link, 
        loop: Optional[Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop]] = None):

        if api_link:
            self._main_loop = loop
            self.o = urlparse(api_link)

            if self.o.scheme=='':
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

    @staticmethod
    def json_to_dict(l):
        dict_answer = {}
        for i in l:
            for j in i:
                dict_answer[j] = i[j]     
        return dict_answer

    async def get_response(self, query):
        loc_session = self.session()
        link = urlunparse(self.o._replace(query=query))

        print(link)

        async with loc_session.get(link) as resp:
            
            if resp.status != 200:
                msg = f"The server returned HTTP {resp.status} {resp.reason}. Response body:\n[{await resp.text()}]"
                await self.close()
                raise RuntimeError(msg)

            answer = await resp.read()

        await self.close()
        return answer

    async def get_user_w_auto(self, user):

        if user.login and user.password:
            
            query = f'xmlagent=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
            answer = await self.get_response(query)

            try:
                answer = user_w_auto(self.json_to_dict(json.loads(answer)))
            except json.decoder.JSONDecodeError:        # Если вернулся XML вместо JSON
                answer = xml.fromstring(answer)
                
                tmp_dict = {}

                for table in answer.iter('userdata'):
                    for row in table:
                        tmp_dict[row.tag] = row.text

                answer = user_w_auto(tmp_dict)

            return answer
            
        else:
            raise ValueError('Login and password should not be NONE')     

    async def get_user_payment(self, user):
        
        if user.login and user.password:

            s: List[user_payment]
            s = []

            #query = f'xmlagent=true&payments=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
            query = f'xmlagent=true&payments=true&json=true'   # debug row
            answer = await self.get_response(query)

            try:
                answer = json.loads(answer)
            except json.decoder.JSONDecodeError:
                answer = xml.fromstring(answer)

                tmp_ans = {}
                rand_index = 0

                for table in answer.iter('payment'):
                    temp_dict = {}
                    for row in table:
                        temp_dict[row.tag] = row.text
                    tmp_ans[rand_index] = temp_dict
                    rand_index += 1
                answer = tmp_ans

            for i in answer:
                answer[i]['date'] = datetime.datetime.strptime(answer[i]['date'],'%Y-%m-%d %H:%M:%S')
                s.append(user_payment(answer[i]))
            return s
            
        else:
            raise ValueError('Login and password should not be NONE')

    #я не уверен, как оно будет работать с несколькокими объявлениями. надо протестировать
    async def get_user_announcement(self, user):

        if user.login and user.password:

            s: List[user_payment]
            s = []

            #query = f'xmlagent=true&announcements=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
            query = f'xmlagent=true&announcements=true&json=true' # debug
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

            return s
            
        else:
            raise ValueError('Login and password should not be NONE')

    # не тестировалось. сайт отправляет не ту страницу + json пока что не работает
    async def get_user_tickets(self, user):

        if user.login and user.password:

            s: List[user_tickets]
            s = []

            #query = f'xmlagent=true&tickets=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
            query = f'xmlagent=true&tickets=true&json=true'  # debug 
            answer = await self.get_response(query)

            try:
                answer = json.loads(answer)
                
            except json.decoder.JSONDecodeError:
                answer = xml.fromstring(answer)
                temp_ans = {}
                index = 0
                for table in answer.iter('ticket'):
                    temp_dict = {}
                    for row in table:
                        temp_dict[row.tag] = row.text
                    temp_ans[index] = user_tickets(temp_dict)
                    index += 1
                answer = temp_ans

            for i in answer:
                answer[i]['date'] = datetime.datetime.strptime(answer[i]['date'],'%Y-%m-%d %H:%M:%S')
                s.append(user_payment(answer[i]))

            return s
            
        else:
            raise ValueError('Login and password should not be NONE')

            

    async def get_user_paument_systems(self, user):

        if user.login and user.password:

            s: List[user_tickets]
            s = []

            query = f'xmlagent=true&opayz=true&json=true&uberlogin={user.login}&uberpassword={user.password}' #
            answer = await self.get_response(query)

            try:
                answer = json.loads(answer)
            except json.decoder.JSONDecodeError:
                answer = xml.fromstring(answer)
                tmp_ans = {}
                index = 0

                for table in answer.iter('paysys'):
                    
                    tmp_dict = {}
                    for row in table:
                        tmp_dict[row.tag] = row.text
                    tmp_ans[index] = tmp_dict
                    index += 1
                answer = tmp_ans

            for i in answer:
                s.append(user_paument_systems(answer[i]))
            
            return s
            
        else:
            raise ValueError('Login and password should not be NONE')


class UserType(dict):
    """
    Объект пользователя
    """

    _id: int
    name: str
    username: Union[str, None]
    whence: str
    ban: bool
    language: str
    reg_date: datetime.datetime
    last_online: datetime.datetime
    login: str
    password: str

    def __init__(self, *args, **kwargs):
        super(UserType, self).__init__(*args, **kwargs)
        self.__dict__ = self



async def main():
    U = UserType({'_id':1,'name':'John','username':'JJJ','login':'gen_xmz0jd4420','password':'ffc13089697dd145be565f0ad593569d'})
    #U = UserType({'_id':1,'name':'fenicu','username':'lolipop','login':'nemmolod30aprouter','password':'925738ee341df2b859794b4237f8a015'})

    B = BillClass('http://demo.ubilling.net.ua:9999/billing/userstats/')
    #B = BillClass('billing-new.nemicom.ua')
    #B = BillClass('https://customer.nemicom.ua')

    ans = await B.get_user_paument_systems(U)
    for i in ans:
        print(i)



if __name__ == "__main__":
    asyncio.run(main())