from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field


class UserInfo(BaseModel):
    """User account information with auto-auth details."""

    billing_login: str = Field(validation_alias="login")
    address: str = ""
    realname: str = ""
    cash: float = 0
    ip: str = ""
    phone: str = ""
    mobile: str = ""
    email: str | None = None
    credit: str = ""
    credit_expire: str | None = Field(default=None, validation_alias="creditexpire")
    pay_id: int = Field(default=0, validation_alias="payid")
    contract: str = ""
    tariff: str = ""
    tariff_alias: str = Field(default="", validation_alias="tariffalias")
    tariff_name: str = Field(default="", validation_alias="tariffnm")
    traffic_download: str = Field(default="", validation_alias="traffdownload")
    traffic_upload: str = Field(default="", validation_alias="traffupload")
    traffic_total: str = Field(default="", validation_alias="trafftotal")
    account_state: str = Field(default="", validation_alias="accountstate")
    account_expire: str | None = Field(default=None, validation_alias="accountexpire")
    currency: str = ""
    version: str = ""

    model_config = {"populate_by_name": True}


class Payment(BaseModel):
    """Single payment record."""

    date: datetime
    summ: str = ""
    balance: str = ""


class FeeCharge(BaseModel):
    """Fee charge (debit) record."""

    date: datetime
    summ: str = ""
    balance: str = ""
    note: str = ""
    type: str = ""


class Announcement(BaseModel):
    """System announcement entry."""

    text: str = Field(default="", validation_alias=AliasChoices("text", "message"))
    unic: str = ""
    title: str = ""


class Ticket(BaseModel):
    """Support ticket."""

    id: int = Field(default=0, validation_alias=AliasChoices("id", "_id"))
    date: datetime
    from_user: str = Field(
        default="", validation_alias=AliasChoices("from", "_from")
    )
    to: str | None = None
    reply_id: int | None = Field(default=None, validation_alias="replyid")
    status: int = 0
    text: str = ""

    model_config = {"populate_by_name": True}


class TicketCreateResult(BaseModel):
    """Result of ticket creation or reply."""

    created: str = ""
    id: int = 0

    @property
    def is_success(self) -> bool:
        return self.created == "success"


class PaymentSystem(BaseModel):
    """Available payment system."""

    name: str = ""
    url: str = ""
    description: str = ""


class CreditInfo(BaseModel):
    """Credit operation result."""

    status: int = 0
    message: str = ""
    full_message: str | None = Field(default=None, validation_alias="fullmessage")
    min_day: int | None = Field(default=None, validation_alias="minday")
    max_day: int | None = Field(default=None, validation_alias="maxday")
    credit_term: int | None = Field(default=None, validation_alias="creditterm")
    credit_price: str | None = Field(default=None, validation_alias="creditprice")
    currency: str | None = None
    credit_intro: str | None = Field(default=None, validation_alias="creditintro")

    model_config = {"populate_by_name": True}


class PayCardResult(BaseModel):
    """Result of pay card activation."""

    result: str = ""
    message: str = ""

    @property
    def is_success(self) -> bool:
        return self.result == "true"


class AgentData(BaseModel):
    """Contractor (agent) assigned to the user."""

    id: int = 0
    bankacc: str = ""
    bankname: str = ""
    bankcode: str = ""
    edrpo: str = ""
    ipn: str = ""
    licensenum: str = ""
    juraddr: str = ""
    phisaddr: str = ""
    phone: str = ""
    contrname: str = ""
    agnameabbr: str = ""
    agsignatory: str = ""
    agsignatory2: str = ""
    agbasis: str = ""
    agmail: str = ""
    siteurl: str = ""


class TariffVService(BaseModel):
    """Tariff or virtual service entry (mixed in one list).

    For tariffs: tariff_name, tariff_price, tariff_days_period are set.
    For virtual services: vservice_name, vservice_price, vservice_days_period are set.
    """

    tariff_name: str | None = Field(default=None, validation_alias="tariffname")
    tariff_price: str | None = Field(default=None, validation_alias="tariffprice")
    tariff_days_period: str | None = Field(
        default=None, validation_alias="tariffdaysperiod"
    )
    vservice_name: str | None = Field(default=None, validation_alias="vsrvname")
    vservice_price: str | None = Field(default=None, validation_alias="vsrvprice")
    vservice_days_period: str | None = Field(
        default=None, validation_alias="vsrvdaysperiod"
    )

    model_config = {"populate_by_name": True}

    @property
    def is_tariff(self) -> bool:
        return self.tariff_name is not None


class AllowedTariff(BaseModel):
    """Tariff available for user to switch to."""

    tariff: str = ""


class FreezeData(BaseModel):
    """User freeze status and parameters."""

    result: str = ""
    message: str = ""
    freeze_self_available: bool | None = Field(
        default=None, validation_alias="freezeSelfAvailable"
    )
    activation_cost: str | None = Field(
        default=None, validation_alias="activationCost"
    )
    tariffs_allowed_list: str | None = Field(
        default=None, validation_alias="tariffsAllowedList"
    )
    tariff_allowed_any: bool | None = Field(
        default=None, validation_alias="tariffAllowedAny"
    )
    negative_balance_freeze_allowed: bool | None = Field(
        default=None, validation_alias="negativeBalanceFreezeAllowed"
    )
    user_balance: str | None = Field(default=None, validation_alias="userBalance")
    user_tariff: str | None = Field(default=None, validation_alias="userTariff")
    user_tariff_freeze_price: str | None = Field(
        default=None, validation_alias="userTariffFreezePrice"
    )
    freeze_status: str | None = Field(default=None, validation_alias="freezeStatus")
    date_from: str | None = Field(default=None, validation_alias="dateFrom")
    date_to: str | None = Field(default=None, validation_alias="dateTo")
    freeze_days_charge_active: bool | None = Field(
        default=None, validation_alias="freezeDaysChargeActive"
    )
    freeze_days_total: str | None = Field(
        default=None, validation_alias="freezeDaysTotal"
    )
    freeze_days_restore: str | None = Field(
        default=None, validation_alias="freezeDaysRestore"
    )
    freeze_days_used: str | None = Field(
        default=None, validation_alias="freezeDaysUsed"
    )
    freeze_days_available: str | None = Field(
        default=None, validation_alias="freezeDaysAvailable"
    )
    freeze_days_worked: str | None = Field(
        default=None, validation_alias="freezeDaysWorked"
    )
    freeze_days_left_to_work: str | None = Field(
        default=None, validation_alias="freezeDaysLeftToWork"
    )

    model_config = {"populate_by_name": True}


class FreezeResult(BaseModel):
    """Result of freeze/unfreeze operation."""

    result: str = ""
    message: str = ""

    @property
    def is_success(self) -> bool:
        return self.result == "Success"
