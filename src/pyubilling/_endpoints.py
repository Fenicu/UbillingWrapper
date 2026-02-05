from base64 import b64encode


class Endpoint:
    """Query parameter builders for each Ubilling XMLAgent endpoint."""

    @staticmethod
    def _base(login: str, password: str) -> dict[str, str]:
        return {
            "xmlagent": "true",
            "json": "true",
            "uberlogin": login,
            "uberpassword": password,
        }

    @classmethod
    def user_info(cls, login: str, password: str) -> dict[str, str]:
        return cls._base(login, password)

    @classmethod
    def just_auth(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "justauth": "true"}

    @classmethod
    def payments(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "payments": "true"}

    @classmethod
    def fee_charges(
        cls,
        login: str,
        password: str,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, str]:
        params = {**cls._base(login, password), "feecharges": "true"}
        if date_from:
            params["datefrom"] = date_from
        if date_to:
            params["dateto"] = date_to
        return params

    @classmethod
    def announcements(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "announcements": "true"}

    @classmethod
    def announcements_read_all(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "annreadall": "true"}

    @classmethod
    def tickets(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "tickets": "true"}

    @classmethod
    def ticket_create(
        cls, login: str, password: str, text: str, *, reply_id: int | None = None
    ) -> dict[str, str]:
        encoded = b64encode(text.encode()).decode()
        params = {
            **cls._base(login, password),
            "ticketcreate": "true",
            "tickettype": "support_request",
            "tickettext": encoded,
        }
        if reply_id is not None:
            params["reply_id"] = str(reply_id)
        return params

    @classmethod
    def signup_request(cls, login: str, password: str) -> dict[str, str]:
        return {
            **cls._base(login, password),
            "ticketcreate": "true",
            "tickettype": "signup_request",
        }

    @classmethod
    def payment_systems(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "opayz": "true"}

    @classmethod
    def agent_assigned(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "agentassigned": "true"}

    @classmethod
    def tariff_vservices(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "tariffvservices": "true"}

    @classmethod
    def tariffs_to_switch(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "tarifftoswitchallowed": "true"}

    @classmethod
    def active_tariffs_vservices(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "activetariffsvservices": "true"}

    @classmethod
    def freeze_data(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "freezedata": "true"}

    @classmethod
    def do_freeze(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "dofreeze": "true"}

    @classmethod
    def do_unfreeze(cls, login: str, password: str) -> dict[str, str]:
        return {**cls._base(login, password), "dounfreeze": "true"}

    @classmethod
    def credit(cls, login: str, password: str) -> dict[str, str]:
        return {
            "module": "creditor",
            "agentcredit": "true",
            "json": "true",
            "uberlogin": login,
            "uberpassword": password,
        }

    @classmethod
    def check_credit(cls, login: str, password: str) -> dict[str, str]:
        return {**cls.credit(login, password), "justcheck": "true"}

    @classmethod
    def pay_card(cls, login: str, password: str, card_number: str) -> dict[str, str]:
        return {
            "module": "paycards",
            "agentpaycards": "true",
            "json": "true",
            "paycard": card_number,
            "uberlogin": login,
            "uberpassword": password,
        }
