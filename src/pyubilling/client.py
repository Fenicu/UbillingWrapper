from __future__ import annotations

import logging

import httpx
from yarl import URL

from pyubilling._endpoints import Endpoint
from pyubilling._parsers import parse_list, parse_single
from pyubilling.exceptions import (
    UbillingAuthError,
    UbillingConnectionError,
    UbillingError,
    UbillingResponseError,
)
from pyubilling.models import (
    AgentData,
    AllowedTariff,
    Announcement,
    CreditInfo,
    FeeCharge,
    FreezeData,
    FreezeResult,
    PayCardResult,
    Payment,
    PaymentSystem,
    TariffVService,
    Ticket,
    TicketCreateResult,
    UserInfo,
)

logger = logging.getLogger("pyubilling")


class UbillingClient:
    """Async client for Ubilling XMLAgent API.

    All API methods require ``login`` and ``password`` parameters.
    ``password`` must be the **MD5 hash** of the user's password,
    not the plaintext password itself.

    If extended authentication is enabled on the server
    (``XMLAGENT_EXTENDED_AUTH_ON``), pass ``uber_key`` — the MD5 hash
    of your Ubilling instance serial number.

    Usage::

        async with UbillingClient("http://demo.ubilling.net.ua:9999/billing/userstats") as client:
            user = await client.get_user_info(
                login="john",
                password="md5_hash_of_password",
            )
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
        uber_key: str | None = None,
    ) -> None:
        url = URL(base_url)
        if url.scheme not in ("http", "https"):
            raise UbillingError(
                f"base_url must use http or https scheme, got: {url.scheme!r}"
            )
        if not url.host:
            raise UbillingError("base_url must contain a valid host")

        self._base_url = str(url)
        self._timeout = timeout
        self._uber_key = uber_key
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> UbillingClient:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise UbillingError(
                "Client is not open. Use 'async with UbillingClient(...) as client:'"
            )
        return self._client

    @staticmethod
    def _validate_credentials(login: str, password: str) -> None:
        if not login or not password:
            raise UbillingAuthError("Both login and password are required")

    def _inject_uber_key(self, params: dict[str, str]) -> dict[str, str]:
        if self._uber_key:
            params["uberkey"] = self._uber_key
        return params

    async def _get(self, params: dict[str, str]) -> bytes:
        client = self._ensure_client()
        params = self._inject_uber_key(params)
        try:
            response = await client.get("", params=params)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise UbillingConnectionError(f"Request timed out: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise UbillingResponseError(
                f"HTTP {exc.response.status_code}: {exc.response.text}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.HTTPError as exc:
            raise UbillingConnectionError(f"Connection error: {exc}") from exc

        logger.debug("GET %s -> %d bytes", response.url, len(response.content))
        return response.content

    async def _post(self, params: dict[str, str], body: dict) -> bytes:
        client = self._ensure_client()
        params = self._inject_uber_key(params)
        try:
            response = await client.post("", params=params, json=body)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise UbillingConnectionError(f"Request timed out: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise UbillingResponseError(
                f"HTTP {exc.response.status_code}: {exc.response.text}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.HTTPError as exc:
            raise UbillingConnectionError(f"Connection error: {exc}") from exc

        logger.debug("POST %s -> %d bytes", response.url, len(response.content))
        return response.content

    # -- User data --

    async def get_user_info(self, login: str, password: str) -> UserInfo | None:
        """Get user account information.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.user_info(login, password))
        return parse_single(raw, UserInfo, root_tag="userdata")

    async def check_auth(self, login: str, password: str) -> bool:
        """Check if credentials are valid without returning user data.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        try:
            await self._get(Endpoint.just_auth(login, password))
            return True
        except UbillingResponseError:
            return False

    # -- Payments & charges --

    async def get_payments(self, login: str, password: str) -> list[Payment]:
        """Get user payment history.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.payments(login, password))
        return parse_list(raw, Payment, root_tag="payment")

    async def get_fee_charges(
        self,
        login: str,
        password: str,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[FeeCharge]:
        """Get fee charge (debit) history.

        Args:
            login: User login.
            password: MD5 hash of user password.
            date_from: Optional start date filter (YYYY-MM-DD).
            date_to: Optional end date filter (YYYY-MM-DD).
        """
        self._validate_credentials(login, password)
        raw = await self._get(
            Endpoint.fee_charges(login, password, date_from=date_from, date_to=date_to)
        )
        return parse_list(raw, FeeCharge, root_tag="feecharge")

    # -- Announcements --

    async def get_announcements(self, login: str, password: str) -> list[Announcement]:
        """Get active announcements for the user.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.announcements(login, password))
        return parse_list(raw, Announcement, root_tag="data")

    async def mark_announcements_read(self, login: str, password: str) -> None:
        """Mark all user announcements as read.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        await self._get(Endpoint.announcements_read_all(login, password))

    # -- Tickets --

    async def get_tickets(self, login: str, password: str) -> list[Ticket]:
        """Get all user support tickets and replies.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.tickets(login, password))
        return parse_list(raw, Ticket, root_tag="ticket")

    async def create_ticket(
        self,
        login: str,
        password: str,
        text: str,
        *,
        reply_id: int | None = None,
    ) -> TicketCreateResult | None:
        """Create a support ticket or reply to an existing one.

        The text is automatically BASE64-encoded before sending.

        Args:
            login: User login.
            password: MD5 hash of user password.
            text: Ticket text (plaintext, will be base64-encoded).
            reply_id: If replying, the ID of the original ticket (not a reply).
        """
        self._validate_credentials(login, password)
        raw = await self._get(
            Endpoint.ticket_create(login, password, text, reply_id=reply_id)
        )
        return parse_single(raw, TicketCreateResult, root_tag="data")

    async def create_signup_request(
        self,
        login: str,
        password: str,
        *,
        date: str,
        ip: str,
        street: str,
        build: str,
        apt: str,
        realname: str,
        phone: str,
        notes: str = "",
    ) -> TicketCreateResult | None:
        """Create a signup (connection) request via POST.

        Args:
            login: User login.
            password: MD5 hash of user password.
            date: Request date (YYYY-MM-DD HH:MM:SS).
            ip: Application IP address.
            street: City and street.
            build: Building number.
            apt: Apartment number.
            realname: Full name.
            phone: Phone number.
            notes: Additional notes.
        """
        self._validate_credentials(login, password)
        body = {
            "date": date,
            "state": 0,
            "ip": ip,
            "street": street,
            "build": build,
            "apt": apt,
            "realname": realname,
            "phone": phone,
            "service": "Internet",
            "notes": notes,
        }
        raw = await self._post(Endpoint.signup_request(login, password), body)
        return parse_single(raw, TicketCreateResult, root_tag="data")

    # -- Payment systems --

    async def get_payment_systems(self, login: str, password: str) -> list[PaymentSystem]:
        """Get available online payment systems (OpenPayz).

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.payment_systems(login, password))
        return parse_list(raw, PaymentSystem, root_tag="paysys")

    # -- Credit --

    async def get_credit(self, login: str, password: str) -> CreditInfo | None:
        """Request a credit for several days.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.credit(login, password))
        return parse_single(raw, CreditInfo, root_tag="data")

    async def check_credit(self, login: str, password: str) -> CreditInfo | None:
        """Check if credit can be set (without actually setting it).

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.check_credit(login, password))
        return parse_single(raw, CreditInfo, root_tag="data")

    # -- Pay cards --

    async def use_pay_card(
        self, login: str, password: str, card_number: str
    ) -> PayCardResult | None:
        """Activate a prepaid card to top up user balance.

        Args:
            login: User login.
            password: MD5 hash of user password.
            card_number: Prepaid card number.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.pay_card(login, password, card_number))
        return parse_single(raw, PayCardResult, root_tag="data")

    # -- Agent / contractor --

    async def get_agent_data(self, login: str, password: str) -> AgentData | None:
        """Get contractor (agent) assigned to the user.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.agent_assigned(login, password))
        return parse_single(raw, AgentData, root_tag="agentdata")

    # -- Tariffs & virtual services --

    async def get_tariff_vservices(
        self, login: str, password: str
    ) -> list[TariffVService]:
        """Get current user tariff and virtual services.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.tariff_vservices(login, password))
        return parse_list(raw, TariffVService, root_tag="tariffvservices")

    async def get_allowed_tariffs(
        self, login: str, password: str
    ) -> list[AllowedTariff]:
        """Get tariffs available for user to switch to.

        Requires tariff switching to be enabled in userstats.ini.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.tariffs_to_switch(login, password))
        return parse_list(raw, AllowedTariff, root_tag="tarifftoswitchallowed")

    async def get_active_tariffs_vservices(
        self, login: str, password: str
    ) -> list[TariffVService]:
        """Get all active (non-archived) tariffs and virtual services.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.active_tariffs_vservices(login, password))
        return parse_list(raw, TariffVService, root_tag="activetariffsvservices")

    # -- Freeze / unfreeze --

    async def get_freeze_data(self, login: str, password: str) -> FreezeData | None:
        """Get user freeze status and parameters.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.freeze_data(login, password))
        return parse_single(raw, FreezeData, root_tag="freezedata")

    async def freeze_user(self, login: str, password: str) -> FreezeResult | None:
        """Freeze the user account.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.do_freeze(login, password))
        return parse_single(raw, FreezeResult, root_tag="dofreeze")

    async def unfreeze_user(self, login: str, password: str) -> FreezeResult | None:
        """Unfreeze the user account.

        Requires XMLAGENT_SELF_UNFREEZE_ALLOWED to be enabled.

        Args:
            login: User login.
            password: MD5 hash of user password.
        """
        self._validate_credentials(login, password)
        raw = await self._get(Endpoint.do_unfreeze(login, password))
        return parse_single(raw, FreezeResult, root_tag="dofreeze")

    # -- Connection check --

    async def check_connection(self) -> bool:
        """Verify the API endpoint is reachable."""
        client = self._ensure_client()
        try:
            response = await client.get("")
            return response.is_success
        except httpx.HTTPError:
            return False
