# pyubilling

Async Python client for the [Ubilling XMLAgent API](http://wiki.ubilling.net.ua/doku.php?id=xmlagent).

## Installation

```bash
uv add git+https://github.com/Fenicu/UbillingWrapper
```

Or with pip:

```bash
pip install git+https://github.com/Fenicu/UbillingWrapper
```

## Authentication

All API methods require `login` and `password` parameters.

> **Important:** `password` must be the **MD5 hash** of the user's password, not the plaintext password.

Example: for password `codr52mv`, pass `614e8c88061bc45a75fdc1b2eefe1e84`.

If extended authentication is enabled on the server (`XMLAGENT_EXTENDED_AUTH_ON`),
pass `uber_key` to the client constructor — the MD5 hash of your Ubilling instance serial number.

## Usage

```python
import asyncio
import hashlib
from pyubilling import UbillingClient

async def main():
    password_md5 = hashlib.md5(b"user_password").hexdigest()

    async with UbillingClient("http://demo.ubilling.net.ua:9999/billing/userstats") as client:
        # User info
        user = await client.get_user_info(login="john", password=password_md5)
        if user:
            print(user.billing_login, user.cash, user.tariff_name)

        # Payments & fee charges
        payments = await client.get_payments(login="john", password=password_md5)
        charges = await client.get_fee_charges(
            login="john", password=password_md5,
            date_from="2024-01-01", date_to="2024-12-31",
        )

        # Announcements
        announcements = await client.get_announcements(login="john", password=password_md5)
        await client.mark_announcements_read(login="john", password=password_md5)

        # Support tickets
        tickets = await client.get_tickets(login="john", password=password_md5)
        result = await client.create_ticket(
            login="john", password=password_md5,
            text="My internet is down",
        )

        # Payment systems & prepaid cards
        pay_systems = await client.get_payment_systems(login="john", password=password_md5)
        card_result = await client.use_pay_card(
            login="john", password=password_md5,
            card_number="2621506348983057",
        )

        # Credit
        credit_check = await client.check_credit(login="john", password=password_md5)
        credit = await client.get_credit(login="john", password=password_md5)

        # Contractor (agent) data
        agent = await client.get_agent_data(login="john", password=password_md5)

        # Tariffs & virtual services
        tariff_info = await client.get_tariff_vservices(login="john", password=password_md5)
        allowed = await client.get_allowed_tariffs(login="john", password=password_md5)
        all_tariffs = await client.get_active_tariffs_vservices(login="john", password=password_md5)

        # Freeze / unfreeze
        freeze_info = await client.get_freeze_data(login="john", password=password_md5)
        freeze_result = await client.freeze_user(login="john", password=password_md5)
        unfreeze_result = await client.unfreeze_user(login="john", password=password_md5)

        # Auth check & connection check
        is_valid = await client.check_auth(login="john", password=password_md5)
        is_alive = await client.check_connection()

asyncio.run(main())
```

### Extended authentication

```python
async with UbillingClient(
    "http://demo.ubilling.net.ua:9999/billing/userstats",
    uber_key="md5_hash_of_serial_number",
) as client:
    ...
```

## API Methods

| Method | Description |
|---|---|
| `get_user_info` | User account information |
| `check_auth` | Validate credentials |
| `get_payments` | Payment history |
| `get_fee_charges` | Fee charge (debit) history with optional date filter |
| `get_announcements` | Active announcements |
| `mark_announcements_read` | Mark all announcements as read |
| `get_tickets` | Support tickets and replies |
| `create_ticket` | Create ticket or reply (text is base64-encoded automatically) |
| `create_signup_request` | Create signup request (POST) |
| `get_payment_systems` | Available online payment systems (OpenPayz) |
| `use_pay_card` | Activate a prepaid card |
| `get_credit` | Request credit |
| `check_credit` | Check credit availability |
| `get_agent_data` | Contractor assigned to the user |
| `get_tariff_vservices` | Current tariff and virtual services |
| `get_allowed_tariffs` | Tariffs available for switching |
| `get_active_tariffs_vservices` | All active tariffs and virtual services (provider-wide) |
| `get_freeze_data` | Freeze status and parameters |
| `freeze_user` | Freeze user account |
| `unfreeze_user` | Unfreeze user account |
| `check_connection` | Check if API is reachable |

## Requirements

- Python >= 3.13
- httpx
- pydantic v2
- yarl
