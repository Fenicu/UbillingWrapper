import aiohttp
from urllib.parse import urlparse, urlunparse
from typing import Optional, Union
import datetime
import asyncio
import json

''' Вопросы
1. Что делать с ошибками? Логировать их или просто принтить?
2. Что надо вернуть? JSON структуру или что-то конкретное?
3. Авторизация с результатом есть только в данных пользователя. 
В других функциях, с авторизацией возвращается путой список.
Как правильно это обработать? Выдать ошибку или так и должно быть?

TO DO
1. XML Agent оключен конфигурацией
2. Вместо JSON возвращать кастомный словарик
'''


class BillClass():

    #Уточнить как приходит ссылка (с http или без)
    def __init__(self, api_link, 
        loop: Optional[Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop]] = None):

        if api_link:
            self._main_loop = loop
            self.o = urlparse(api_link)

            if self.o.scheme=='':
                self.o = self.o._replace(scheme='http',netloc=self.o.path,path='')

            self._session: Optional[aiohttp.ClientSession] = None

        else:
            raise ValueError('api_link should not be NONE')

    def get_new_session(self):
        return aiohttp.ClientSession()

    def loop(self):
        return self._main_loop

    def session(self):
        if self._session is None or self._session.closed:
            self._session = self.get_new_session()
        return self._session

    async def close(self):
        await self._session.close()

    async def get_user_w_auto(self, user):

        try:

            if user.login and user.password:

                loc_session = self.session()
                path = 'billing/userstats/'
                query = f'xmlagent=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
                b = urlunparse(self.o._replace(path=path,query=query))

                async with loc_session.get(b) as resp:
                    answer = await resp.read()
                answer = json.loads(answer)

                return answer # perhaps надо будет заменить
                
            else:
                raise ValueError('Login and password should not be NONE')
        except Exception as e:
            print(e)
        finally:
            await self.close()

    async def get_user_payment(self, user):

        try:

            if user.login and user.password:

                loc_session = self.session()
                path = 'billing/userstats/'
                query = f'xmlagent=true&payments=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
                b = urlunparse(self.o._replace(path=path,query=query))

                async with loc_session.get(b) as resp:
                    answer = await resp.read()
                answer = json.loads(answer)

                return answer # perhaps надо будет заменить
                
            else:
                raise ValueError('Login and password should not be NONE. Or should be. Dunno')

        except Exception as e:
            print(e)
        finally:
            await self.close()

    async def get_user_announcement(self, user):

        try:

            if user.login and user.password:

                loc_session = self.session()
                path = 'billing/userstats/'
                query = f'xmlagent=true&announcements=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
                b = urlunparse(self.o._replace(path=path,query=query))

                async with loc_session.get(b) as resp:
                    answer = await resp.read()
                answer = json.loads(answer)

                return answer # perhaps надо будет заменить
                
            else:
                raise ValueError('Login and password should not be NONE')
        except Exception as e:
            print(e)
        finally:
            await self.close()
    
    async def get_user_tickets(self, user):

        try:

            if user.login and user.password:

                loc_session = self.session()
                path = 'billing/userstats/'
                query = f'xmlagent=true&tickets=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
                b = urlunparse(self.o._replace(path=path,query=query))

                async with loc_session.get(b) as resp:
                    answer = await resp.read()
                answer = json.loads(answer)

                return answer # perhaps надо будет заменить
                
            else:
                raise ValueError('Login and password should not be NONE')
        except Exception as e:
            print(e)
        finally:
            await self.close()

    async def get_user_paument_systems(self, user):

        try:

            if user.login and user.password:

                loc_session = self.session()
                path = 'billing/userstats/'
                query = f'xmlagent=true&opayz=true&json=true&uberlogin={user.login}&uberpassword={user.password}'
                b = urlunparse(self.o._replace(path=path,query=query))

                async with loc_session.get(b) as resp:
                    answer = await resp.read()
                answer = json.loads(answer)

                return answer # perhaps надо будет заменить
                
            else:
                raise ValueError('Login and password should not be NONE')
        except Exception as e:
            print(e)
        finally:
            await self.close()

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

    B = BillClass('demo.ubilling.net.ua:9999')
    print(await B.get_user_payment(U))

if __name__ == "__main__":
    asyncio.run(main())