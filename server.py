"""
JugaadX MCP Server — Multi-Account Edition
===========================================
A complete MCP server built on the official DoubleTick Public API
(the backend powering JugaadX).

Base URL: https://public.doubletick.io
Docs: https://docs.doubletick.io

Multi-account support: each account is identified by a short name (e.g. 'afton').
API keys and WABA numbers are stored as environment variables — never in code.

ENV VARIABLE FORMAT:
    <ACCOUNT_NAME>_API_KEY   → API key for that account
    <ACCOUNT_NAME>_WABA      → WhatsApp Business number for that account

Example for an account named "afton":
    AFTON_API_KEY = key_abc123
    AFTON_WABA    = +919884016960

To add more accounts, just add more env variables and register them in ACCOUNT_NAMES list below.
"""

import httpx
import json
import os
from mcp.server.fastmcp import FastMCP

# ─────────────────────────────────────────────
# MCP Server Initialization
# ─────────────────────────────────────────────
mcp = FastMCP("JugaadX")

BASE_URL = "https://public.doubletick.io"

# ─────────────────────────────────────────────
# MULTI-ACCOUNT CONFIGURATION
# Add your account short names here.
# For each name, set <NAME>_API_KEY and <NAME>_WABA as env variables on Render.
# ─────────────────────────────────────────────
ACCOUNT_NAMES = [
    "jugaad_main",
    "afton",
    # "client3",   ← uncomment and add env vars to add more
    # "client4",
]

def _load_accounts() -> dict:
    accounts = {}
    for name in ACCOUNT_NAMES:
        env_prefix = name.upper()
        api_key = os.environ.get(f"{env_prefix}_API_KEY")
        waba    = os.environ.get(f"{env_prefix}_WABA")
        if api_key and waba:
            accounts[name] = {"api_key": api_key, "waba": waba}
        else:
            print(f"⚠️  Warning: Account '{name}' is missing env vars "
                  f"({env_prefix}_API_KEY / {env_prefix}_WABA) — skipping.")
    return accounts

ACCOUNTS = _load_accounts()


def get_account(account_name: str) -> dict:
    """Resolve account name → {api_key, waba}. Raises clear error if unknown."""
    account = ACCOUNTS.get(account_name.lower())
    if not account:
        available = list(ACCOUNTS.keys())
        raise ValueError(
            f"Unknown account: '{account_name}'. "
            f"Available accounts: {available}. "
            f"To add a new account, set <NAME>_API_KEY and <NAME>_WABA env vars on Render."
        )
    return account


def _headers(api_key: str) -> dict:
    return {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ─────────────────────────────────────────────
# HTTP Helpers
# ─────────────────────────────────────────────

def api_get(path: str, api_key: str, params: dict = None) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{BASE_URL}{path}", headers=_headers(api_key), params=params)
        resp.raise_for_status()
        return resp.json()


def api_post(path: str, api_key: str, payload: dict = None) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{BASE_URL}{path}", headers=_headers(api_key), json=payload or {})
        resp.raise_for_status()
        return resp.json()


def api_patch(path: str, api_key: str, payload: dict = None) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.patch(f"{BASE_URL}{path}", headers=_headers(api_key), json=payload or {})
        resp.raise_for_status()
        return resp.json()


def api_delete(path: str, api_key: str, payload: dict = None) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.request("DELETE", f"{BASE_URL}{path}", headers=_headers(api_key), json=payload or {})
        resp.raise_for_status()
        return resp.json()


# ═══════════════════════════════════════════════════════════════════
# 🔍 ACCOUNT INFO
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def list_accounts() -> str:
    """
    List all configured JugaadX accounts available on this MCP server.
    Use this to see which account names you can pass to other tools.
    """
    if not ACCOUNTS:
        return json.dumps({"error": "No accounts configured. Add env vars on Render."})
    result = {
        name: {"waba": info["waba"], "api_key": "***hidden***"}
        for name, info in ACCOUNTS.items()
    }
    return json.dumps({"configured_accounts": result}, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 📨 SECTION 1: OUTGOING MESSAGES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def send_template_message(
    to_number: str,
    template_name: str,
    account_name: str,
    language_code: str = "en",
    components: list = None
) -> str:
    """
    Send a WhatsApp Template message to a customer.

    Args:
        to_number: Recipient phone number with country code (e.g. 919876543210)
        template_name: Name of the approved WhatsApp template
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        language_code: Language code (default: 'en')
        components: Optional templateData list for dynamic variables/buttons
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/message/template", acc["api_key"], {
        "messages": [
            {
                "to": to_number,
                "from": acc["waba"],
                "content": {
                    "templateName": template_name,
                    "language": language_code,
                    "templateData": components or {}
                }
            }
        ]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_text_message(
    to_number: str,
    message: str,
    account_name: str
) -> str:
    """
    Send a plain WhatsApp text message to a customer.

    Args:
        to_number: Recipient phone number with country code (e.g. 919876543210)
        message: The text content to send
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/message/text", acc["api_key"], {
        "to": to_number,
        "from": acc["waba"],
        "content": {"text": message}
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_video_message(
    to_number: str,
    video_url: str,
    account_name: str,
    caption: str = ""
) -> str:
    """
    Send a WhatsApp video message to a customer.

    Args:
        to_number: Recipient phone number with country code
        video_url: Public URL of the video file (MP4)
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        caption: Optional caption text
    """
    acc = get_account(account_name)
    payload = {
        "to": to_number,
        "from": acc["waba"],
        "content": {"mediaUrl": video_url}
    }
    if caption:
        payload["content"]["caption"] = caption
    result = api_post("/whatsapp/message/video", acc["api_key"], payload)
    return json.dumps(result, indent=2)


@mcp.tool()
def send_audio_message(
    to_number: str,
    audio_url: str,
    account_name: str
) -> str:
    """
    Send a WhatsApp audio message to a customer.

    Args:
        to_number: Recipient phone number with country code
        audio_url: Public URL of the audio file (MP3)
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/message/audio", acc["api_key"], {
        "to": to_number,
        "from": acc["waba"],
        "content": {"mediaUrl": audio_url}
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_image_message(
    to_number: str,
    image_url: str,
    account_name: str,
    caption: str = ""
) -> str:
    """
    Send a WhatsApp image message to a customer.

    Args:
        to_number: Recipient phone number with country code
        image_url: Public URL of the image (JPG, PNG, WEBP)
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        caption: Optional caption text
    """
    acc = get_account(account_name)
    payload = {
        "to": to_number,
        "from": acc["waba"],
        "content": {"mediaUrl": image_url}
    }
    if caption:
        payload["content"]["caption"] = caption
    result = api_post("/whatsapp/message/image", acc["api_key"], payload)
    return json.dumps(result, indent=2)


@mcp.tool()
def send_document_message(
    to_number: str,
    document_url: str,
    filename: str,
    account_name: str,
    caption: str = ""
) -> str:
    """
    Send a WhatsApp document/PDF to a customer.

    Args:
        to_number: Recipient phone number with country code
        document_url: Public URL of the document
        filename: Display name for the file (e.g. 'invoice.pdf')
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        caption: Optional caption text
    """
    acc = get_account(account_name)
    payload = {
        "to": to_number,
        "from": acc["waba"],
        "content": {"mediaUrl": document_url, "filename": filename}
    }
    if caption:
        payload["content"]["caption"] = caption
    result = api_post("/whatsapp/message/document", acc["api_key"], payload)
    return json.dumps(result, indent=2)


@mcp.tool()
def send_location_message(
    to_number: str,
    latitude: float,
    longitude: float,
    account_name: str,
    name: str = "",
    address: str = ""
) -> str:
    """
    Send a WhatsApp location pin to a customer.

    Args:
        to_number: Recipient phone number with country code
        latitude: Latitude coordinate (e.g. 13.0827)
        longitude: Longitude coordinate (e.g. 80.2707)
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        name: Optional location name (e.g. 'Our Office')
        address: Optional address string
    """
    acc = get_account(account_name)
    content = {"latitude": latitude, "longitude": longitude}
    if name:
        content["name"] = name
    if address:
        content["address"] = address
    result = api_post("/whatsapp/message/location", acc["api_key"], {
        "to": to_number,
        "from": acc["waba"],
        "content": content
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_interactive_button_message(
    to_number: str,
    body_text: str,
    buttons: list,
    account_name: str,
    header_text: str = "",
    footer_text: str = ""
) -> str:
    """
    Send a WhatsApp interactive message with clickable buttons.

    Args:
        to_number: Recipient phone number with country code
        body_text: Main message body text
        buttons: List of button dicts, each with 'id' and 'title' (max 3).
                 Example: [{"id": "yes_btn", "title": "Yes"}, {"id": "no_btn", "title": "No"}]
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        header_text: Optional header text
        footer_text: Optional footer text
    """
    acc = get_account(account_name)
    content = {"body": body_text, "buttons": buttons}
    if header_text:
        content["header"] = header_text
    if footer_text:
        content["footer"] = footer_text
    result = api_post("/whatsapp/message/interactive", acc["api_key"], {
        "to": to_number,
        "from": acc["waba"],
        "content": content
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_interactive_list_message(
    to_number: str,
    body_text: str,
    button_label: str,
    sections: list,
    account_name: str,
    header_text: str = "",
    footer_text: str = ""
) -> str:
    """
    Send a WhatsApp interactive list message with a dropdown menu.

    Args:
        to_number: Recipient phone number with country code
        body_text: Main message body text
        button_label: Label on the button that opens the list (e.g. 'Choose Option')
        sections: List of section dicts. Each section has 'title' and 'rows'.
                  Each row has 'id', 'title', and optional 'description'.
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        header_text: Optional header text
        footer_text: Optional footer text
    """
    acc = get_account(account_name)
    content = {"body": body_text, "button": button_label, "sections": sections}
    if header_text:
        content["header"] = header_text
    if footer_text:
        content["footer"] = footer_text
    result = api_post("/whatsapp/message/interactive-list", acc["api_key"], {
        "to": to_number,
        "from": acc["waba"],
        "content": content
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 💬 SECTION 2: CHAT MESSAGES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def export_chats_to_excel(
    customer_number: str,
    account_name: str,
    start_date: str = "",
    end_date: str = "",
    include_media: bool = True
) -> str:
    """
    Export all chat messages for a customer to Excel format.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        start_date: Start date in DD-MM-YYYY format (optional)
        end_date: End date in DD-MM-YYYY format (optional)
        include_media: Whether to include media files (default: True)
    """
    acc = get_account(account_name)
    payload = {
        "wabaNumber": acc["waba"],
        "customerPhoneNumber": customer_number,
        "includeMedia": include_media,
    }
    if start_date:
        payload["startDate"] = start_date
    if end_date:
        payload["endDate"] = end_date
    result = api_post("/export-chats", acc["api_key"], payload)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_chat_messages(
    customer_number: str,
    account_name: str,
    start_date: str = "",
    end_date: str = ""
) -> str:
    """
    Get chat message history for a specific customer.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        start_date: Start date in DD-MM-YYYY format (optional)
        end_date: End date in DD-MM-YYYY format (optional)
    """
    acc = get_account(account_name)
    params = {"customerNumber": customer_number, "wabaNumber": acc["waba"]}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    result = api_get("/chat-messages", acc["api_key"], params=params)
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 📢 SECTION 3: BROADCAST GROUPS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def send_broadcast_message(
    group_name: str,
    template_name: str,
    account_name: str,
    language_code: str = "en",
    template_data: dict = None
) -> str:
    """
    Send a WhatsApp template message to an entire broadcast group.

    Args:
        group_name: The name of the broadcast group to send to
        template_name: Name of the approved template to use
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        language_code: Language code (default: 'en')
        template_data: Optional templateData dict for dynamic variables
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/message/broadcast", acc["api_key"], {
        "groupName": group_name,
        "from": acc["waba"],
        "content": {
            "templateName": template_name,
            "language": language_code,
            "templateData": template_data or {}
        }
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def create_broadcast_group(
    name: str,
    account_name: str,
    members: list = None
) -> str:
    """
    Create a new broadcast group.

    Args:
        name: Name for the broadcast group (e.g. 'April Offer Campaign')
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        members: Optional list of member dicts with 'name' and 'phone' keys.
                 Example: [{"name": "John", "phone": "919876543210"}]
    """
    acc = get_account(account_name)
    result = api_post("/groups", acc["api_key"], {
        "name": name,
        "members": members or []
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def delete_broadcast_groups(
    group_ids: list,
    account_name: str
) -> str:
    """
    Delete one or more broadcast groups.

    Args:
        group_ids: List of group IDs to delete
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_delete("/groups", acc["api_key"], {"groupIds": group_ids})
    return json.dumps(result, indent=2)


@mcp.tool()
def get_broadcast_groups(
    account_name: str,
    search_query: str = "",
    order_by: str = "DATE_CREATED",
    order_format: str = "DESCENDING"
) -> str:
    """
    Get a paginated list of all broadcast groups.

    Args:
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        search_query: Optional search query to filter groups by name
        order_by: Field to order by: 'NAME' or 'DATE_CREATED' (default: 'DATE_CREATED')
        order_format: Order direction: 'ASCENDING' or 'DESCENDING' (default: 'DESCENDING')
    """
    acc = get_account(account_name)
    params = {"orderBy": order_by, "format": order_format}
    if search_query:
        params["searchQuery"] = search_query
    result = api_get("/groups", acc["api_key"], params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
def add_members_to_broadcast_group(
    group_id: str,
    members: list,
    account_name: str
) -> str:
    """
    Add members (phone numbers) to an existing broadcast group.

    Args:
        group_id: The ID of the broadcast group
        members: List of member dicts with 'name' (optional) and 'phone' (required).
                 Example: [{"name": "John", "phone": "919876543210"}]
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/groups/add-members", acc["api_key"], {
        "groupId": group_id,
        "members": members
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 📋 SECTION 4: TEMPLATES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def create_template(
    name: str,
    category: str,
    language: str,
    body_text: str,
    account_name: str,
    header_text: str = "",
    header_format: str = "TEXT",
    footer_text: str = "",
    buttons: list = None
) -> str:
    """
    Create a new WhatsApp message template (will be sent to Meta for approval).

    Args:
        name: Template name — lowercase, underscores only (e.g. 'order_confirmation')
        category: 'MARKETING' or 'UTILITY'
        language: Language code (e.g. 'en', 'hi', 'ta')
        body_text: Main body. Use {{1}}, {{2}} etc. for dynamic variables.
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        header_text: Optional header text
        header_format: Header format: 'TEXT', 'IMAGE', 'VIDEO', 'DOCUMENT' (default: 'TEXT')
        footer_text: Optional footer text (e.g. 'Reply STOP to unsubscribe')
        buttons: Optional list of button dicts.
                 Example: [{"type": "URL", "text": "Visit", "url": "https://example.com"}]
                 or [{"type": "QUICK_REPLY", "text": "Yes"}]
    """
    acc = get_account(account_name)
    components = {"body": {"text": body_text}}
    if header_text or header_format != "TEXT":
        components["header"] = {"format": header_format, "text": header_text}
    if footer_text:
        components["footer"] = {"text": footer_text}
    if buttons:
        components["buttons"] = buttons
    result = api_post("/template", acc["api_key"], {
        "name": name,
        "category": category,
        "language": language,
        "wabaNumbers": [acc["waba"]],
        "allowCategoryUpdate": True,
        "components": components
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def delete_template(
    template_name: str,
    account_name: str
) -> str:
    """
    Delete a WhatsApp message template.

    Args:
        template_name: Name of the template to delete
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_delete("/template", acc["api_key"], {
        "name": template_name,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def edit_template(
    template_name: str,
    account_name: str,
    body_text: str = "",
    footer_text: str = ""
) -> str:
    """
    Edit an existing WhatsApp template.

    Args:
        template_name: Name of the template to edit
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        body_text: New body text (use {{1}}, {{2}} for variables)
        footer_text: New footer text
    """
    acc = get_account(account_name)
    payload = {"name": template_name, "wabaNumber": acc["waba"]}
    if body_text:
        payload["body"] = body_text
    if footer_text:
        payload["footer"] = footer_text
    result = api_patch("/template", acc["api_key"], payload)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_templates(account_name: str) -> str:
    """
    Get all WhatsApp message templates for an account.

    Args:
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/template", acc["api_key"], params={"wabaNumber": acc["waba"]})
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 👥 SECTION 5: CUSTOMER
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_customer_details(
    customer_number: str,
    account_name: str
) -> str:
    """
    Get full details of a specific customer.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/whatsapp/customer", acc["api_key"], params={
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def assign_tags_and_custom_fields(
    customer_number: str,
    account_name: str,
    tags: list = None,
    custom_fields: dict = None
) -> str:
    """
    Assign tags and/or custom field values to a customer.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        tags: List of tag strings to assign (e.g. ['Hot Lead', 'VIP'])
        custom_fields: Dict of custom field key-value pairs
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/customer/assign", acc["api_key"], {
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"],
        "tags": tags or [],
        "customFields": custom_fields or {}
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def remove_tags_and_custom_fields(
    customer_number: str,
    account_name: str,
    tags: list = None,
    custom_field_keys: list = None
) -> str:
    """
    Remove tags and/or custom fields from a customer.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        tags: List of tag strings to remove
        custom_field_keys: List of custom field keys to remove
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/customer/remove", acc["api_key"], {
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"],
        "tags": tags or [],
        "customFieldKeys": custom_field_keys or []
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def block_customer(customer_number: str, account_name: str) -> str:
    """
    Block a customer — they will no longer be able to send messages.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/customer/block", acc["api_key"], {
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def unblock_customer(customer_number: str, account_name: str) -> str:
    """
    Unblock a previously blocked customer.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/customer/unblock", acc["api_key"], {
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def check_reverted_on_time(customer_number: str, account_name: str) -> str:
    """
    Check if a customer reverted/replied within the SLA time window.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/whatsapp/customer/reverted-on-time", acc["api_key"], params={
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def assign_team_member_to_customer(
    customer_number: str,
    member_id: str,
    account_name: str
) -> str:
    """
    Assign a team member/agent to a specific customer.

    Args:
        customer_number: Customer's phone number with country code
        member_id: ID of the team member to assign
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/customer/assign-member", acc["api_key"], {
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"],
        "memberId": member_id
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_chat_window_status(customer_number: str, account_name: str) -> str:
    """
    Check if the 24-hour chat window is open for a customer.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/whatsapp/customer/chat-window-status", acc["api_key"], params={
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 👨‍💼 SECTION 6: TEAM MEMBER (CHAT ASSIGNMENT)
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def assign_team_member_to_chat(
    customer_number: str,
    member_id: str,
    account_name: str
) -> str:
    """
    Assign a team member to handle a specific customer chat.

    Args:
        customer_number: Customer's phone number with country code
        member_id: ID of the team member to assign
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/chat/assign-member", acc["api_key"], {
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"],
        "memberId": member_id
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def unassign_team_member_from_chat(customer_number: str, account_name: str) -> str:
    """
    Remove the team member assignment from a customer chat.

    Args:
        customer_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/chat/unassign-member", acc["api_key"], {
        "customerNumber": customer_number,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def logout_team_member(member_id: str, account_name: str) -> str:
    """
    Log out a team member from all their active devices.

    Args:
        member_id: ID of the team member to log out
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/team/logout", acc["api_key"], {
        "memberId": member_id,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 💰 SECTION 7: WALLET
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_wallet_balance(account_name: str) -> str:
    """
    Get the current wallet/credit balance for a JugaadX account.

    Args:
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/whatsapp/wallet/balance", acc["api_key"], params={"wabaNumber": acc["waba"]})
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 👥 SECTION 8: TEAMS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_team(account_name: str) -> str:
    """
    Get all team members in a JugaadX account.

    Args:
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/whatsapp/team", acc["api_key"], params={"wabaNumber": acc["waba"]})
    return json.dumps(result, indent=2)


@mcp.tool()
def change_reporting_manager(
    member_id: str,
    manager_id: str,
    account_name: str
) -> str:
    """
    Change the reporting manager for a team member.

    Args:
        member_id: ID of the team member
        manager_id: ID of the new reporting manager
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_patch("/whatsapp/team/reporting-manager", acc["api_key"], {
        "memberId": member_id,
        "managerId": manager_id,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def remove_team_member(member_id: str, account_name: str) -> str:
    """
    Remove a team member from a JugaadX account.

    Args:
        member_id: ID of the team member to remove
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_delete("/whatsapp/team/member", acc["api_key"], {
        "memberId": member_id,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def add_member_under_reporting_manager(
    manager_id: str,
    member_id: str,
    account_name: str
) -> str:
    """
    Add a team member under a specific reporting manager.

    Args:
        manager_id: ID of the reporting manager
        member_id: ID of the team member to place under this manager
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/team/reporting-manager/member", acc["api_key"], {
        "managerId": manager_id,
        "memberId": member_id,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_team_member_details(member_id: str, account_name: str) -> str:
    """
    Get full details of a specific team member.

    Args:
        member_id: ID of the team member
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/whatsapp/team/member", acc["api_key"], params={
        "memberId": member_id,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 🎭 SECTION 9: ROLES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_all_roles(account_name: str) -> str:
    """
    Get all available roles and their permissions in a JugaadX account.

    Args:
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/whatsapp/roles", acc["api_key"], params={"wabaNumber": acc["waba"]})
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 🖼️ SECTION 10: MEDIA
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def upload_media(
    file_url: str,
    media_type: str,
    account_name: str
) -> str:
    """
    Upload a media file to JugaadX to get a media ID for use in messages.

    Args:
        file_url: Public URL of the media file to upload
        media_type: Type of media: 'image', 'video', 'audio', 'document'
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/media/upload", acc["api_key"], {
        "fileUrl": file_url,
        "mediaType": media_type,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 🔔 SECTION 11: WEBHOOKS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def register_webhook(
    url: str,
    triggers: list,
    account_name: str
) -> str:
    """
    Register a new webhook to receive real-time JugaadX events.

    Args:
        url: Your endpoint URL that will receive webhook POST requests
        triggers: List of event triggers. Options: 'message_status_update',
                  'message_received', 'chat_assigned', 'chat_unassigned',
                  'lead_received_from_widget', 'first_time_message',
                  'customer_custom_field_updated', 'template_updated',
                  'tag_added', 'tag_removed'
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/webhook", acc["api_key"], {
        "url": url,
        "wabaNumber": acc["waba"],
        "triggers": triggers
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_webhooks(account_name: str) -> str:
    """
    Get all registered webhooks for an account.

    Args:
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/whatsapp/webhook", acc["api_key"], params={"wabaNumber": acc["waba"]})
    return json.dumps(result, indent=2)


@mcp.tool()
def delete_webhooks(webhook_ids: list, account_name: str) -> str:
    """
    Delete one or more registered webhooks.

    Args:
        webhook_ids: List of webhook IDs to delete
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_delete("/whatsapp/webhook", acc["api_key"], {
        "webhookIds": webhook_ids,
        "wabaNumber": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def edit_webhook(
    webhook_id: str,
    account_name: str,
    url: str = "",
    triggers: list = None
) -> str:
    """
    Edit an existing webhook's URL or triggers.

    Args:
        webhook_id: ID of the webhook to edit
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
        url: New endpoint URL (leave empty to keep unchanged)
        triggers: New list of triggers (leave empty to keep unchanged)
    """
    acc = get_account(account_name)
    payload = {"webhookId": webhook_id, "wabaNumber": acc["waba"]}
    if url:
        payload["url"] = url
    if triggers:
        payload["triggers"] = triggers
    result = api_post("/whatsapp/webhook/edit", acc["api_key"], payload)
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 📞 SECTION 12: WHATSAPP CALLS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def create_outgoing_call(to_number: str, account_name: str) -> str:
    """
    Initiate an outgoing WhatsApp voice call to a customer.

    Args:
        to_number: Customer's phone number with country code
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_post("/whatsapp/call/outgoing", acc["api_key"], {
        "to": to_number,
        "from": acc["waba"]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_call_permissions(account_name: str) -> str:
    """
    Check WhatsApp calling permissions for an account.

    Args:
        account_name: Account to use (e.g. 'afton', 'jugaad_main'). Use list_accounts() to see options.
    """
    acc = get_account(account_name)
    result = api_get("/whatsapp/call/permissions", acc["api_key"], params={"wabaNumber": acc["waba"]})
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 🚀 Run the server
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("🚀 JugaadX MCP Server (Multi-Account) starting...")
    print(f"📡 Base URL: {BASE_URL}")
    print(f"✅ Loaded accounts: {list(ACCOUNTS.keys()) or 'None — check env vars!'}")
    print("🛠️  All tools ready!\n")
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=port)
