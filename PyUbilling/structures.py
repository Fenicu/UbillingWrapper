import datetime
from typing import Union


class user_w_auto(dict):

    address: str
    realname: str
    bil_login: Union[str, None]
    cash: int
    ip: str
    phone: str
    mobile: str
    email: Union[str, None]
    credit: str
    creditexpire: Union[datetime.datetime, str]
    payid: int
    contract: str
    tariff: str
    tariffnm: str
    traffdownload: str
    traffupload: str
    trafftotal: str
    accountstate: str
    accountexpire: Union[int, str]
    currency: str
    version: str

    def __init__(self, *args, **kwargs):
        super(user_w_auto, self).__init__(*args, **kwargs)
        self.__dict__ = self
        self.bil_login = self.login
        del self["login"]


class user_payment(dict):

    date: datetime.datetime
    summ: str
    balance: str

    def __init__(self, *args, **kwargs):
        super(user_payment, self).__init__(*args, **kwargs)
        self.__dict__ = self


# Посмотреть как оно будет выглядеть в json
class user_announcement(dict):

    text: str
    unic: str
    title: str

    def __init__(self, *args, **kwargs):
        super(user_announcement, self).__init__(*args, **kwargs)
        self.__dict__ = self


class user_tickets(dict):

    _id: int
    date: datetime.datetime
    _from: str
    to: str
    replyid: int
    status: int
    text: str

    def __init__(self, *args, **kwargs):
        super(user_tickets, self).__init__(*args, **kwargs)
        self.__dict__ = self


class user_paument_systems(dict):

    name: str
    url: str
    description: str

    def __init__(self, *args, **kwargs):
        super(user_paument_systems, self).__init__(*args, **kwargs)
        self.__dict__ = self


class user_credit(dict):

    status: int
    message: str

    def __init__(self, *args, **kwargs):
        super(user_credit, self).__init__(*args, **kwargs)
        self.__dict__ = self
