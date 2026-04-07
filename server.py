"""
JugaadX MCP Server
==================
A complete MCP server built on the official DoubleTick Public API
(the backend powering JugaadX).

Base URL: https://public.doubletick.io
Docs: https://docs.doubletick.io

Author: Built with ❤️ using the MCP Python SDK
Usage: python server.py
"""

import httpx
import json
import os
from mcp.server.fastmcp import FastMCP

# ─────────────────────────────────────────────
# MCP Server Initialization
# ─────────────────────────────────────────────
mcp = FastMCP("JugaadX")

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
JUGAADX_API_KEY = os.environ.get("JUGAADX_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://public.doubletick.io"

HEADERS = {
    "Authorization": f"Bearer {JUGAADX_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def api_get(path: str, params: dict = None) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{BASE_URL}{path}", headers=HEADERS, params=params)
        resp.raise_for_status()
        return resp.json()


def api_post(path: str, payload: dict = None) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{BASE_URL}{path}", headers=HEADERS, json=payload or {})
        resp.raise_for_status()
        return resp.json()


def api_patch(path: str, payload: dict = None) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.patch(f"{BASE_URL}{path}", headers=HEADERS, json=payload or {})
        resp.raise_for_status()
        return resp.json()


def api_delete(path: str, payload: dict = None) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.request("DELETE", f"{BASE_URL}{path}", headers=HEADERS, json=payload or {})
        resp.raise_for_status()
        return resp.json()


# ═══════════════════════════════════════════════════════════════════
# 📨 SECTION 1: OUTGOING MESSAGES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def send_template_message(
    to_number: str,
    waba_number: str,
    template_name: str,
    language_code: str = "en",
    components: list = None
) -> str:
    """
    Send a WhatsApp Template message to a customer.

    Args:
        to_number: Recipient phone number with country code (e.g. 919876543210)
        waba_number: Your WhatsApp Business number registered on JugaadX
        template_name: Name of the approved WhatsApp template
        language_code: Language code (default: 'en')
        components: Optional list of component objects for dynamic variables/buttons
    """
    result = api_post("/whatsapp/message/template", {
        "to": to_number,
        "from": waba_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
            "components": components or []
        }
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_text_message(
    to_number: str,
    waba_number: str,
    message: str
) -> str:
    """
    Send a plain WhatsApp text message to a customer.

    Args:
        to_number: Recipient phone number with country code (e.g. 919876543210)
        waba_number: Your WhatsApp Business number registered on JugaadX
        message: The text content to send
    """
    result = api_post("/whatsapp/message/text", {
        "to": to_number,
        "from": waba_number,
        "type": "text",
        "text": {"body": message}
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_video_message(
    to_number: str,
    waba_number: str,
    video_url: str,
    caption: str = ""
) -> str:
    """
    Send a WhatsApp video message to a customer.

    Args:
        to_number: Recipient phone number with country code
        waba_number: Your WhatsApp Business number
        video_url: Public URL of the video file
        caption: Optional caption text
    """
    result = api_post("/whatsapp/message/video", {
        "to": to_number,
        "from": waba_number,
        "type": "video",
        "video": {"link": video_url, "caption": caption}
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_audio_message(
    to_number: str,
    waba_number: str,
    audio_url: str
) -> str:
    """
    Send a WhatsApp audio message to a customer.

    Args:
        to_number: Recipient phone number with country code
        waba_number: Your WhatsApp Business number
        audio_url: Public URL of the audio file
    """
    result = api_post("/whatsapp/message/audio", {
        "to": to_number,
        "from": waba_number,
        "type": "audio",
        "audio": {"link": audio_url}
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_image_message(
    to_number: str,
    waba_number: str,
    image_url: str,
    caption: str = ""
) -> str:
    """
    Send a WhatsApp image message to a customer.

    Args:
        to_number: Recipient phone number with country code
        waba_number: Your WhatsApp Business number
        image_url: Public URL of the image
        caption: Optional caption text
    """
    result = api_post("/whatsapp/message/image", {
        "to": to_number,
        "from": waba_number,
        "type": "image",
        "image": {"link": image_url, "caption": caption}
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_document_message(
    to_number: str,
    waba_number: str,
    document_url: str,
    filename: str,
    caption: str = ""
) -> str:
    """
    Send a WhatsApp document/PDF to a customer.

    Args:
        to_number: Recipient phone number with country code
        waba_number: Your WhatsApp Business number
        document_url: Public URL of the document
        filename: Display name for the file (e.g. 'invoice.pdf')
        caption: Optional caption text
    """
    result = api_post("/whatsapp/message/document", {
        "to": to_number,
        "from": waba_number,
        "type": "document",
        "document": {"link": document_url, "filename": filename, "caption": caption}
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_location_message(
    to_number: str,
    waba_number: str,
    latitude: float,
    longitude: float,
    name: str = "",
    address: str = ""
) -> str:
    """
    Send a WhatsApp location pin to a customer.

    Args:
        to_number: Recipient phone number with country code
        waba_number: Your WhatsApp Business number
        latitude: Latitude coordinate (e.g. 13.0827)
        longitude: Longitude coordinate (e.g. 80.2707)
        name: Optional location name (e.g. 'Our Office')
        address: Optional address string
    """
    result = api_post("/whatsapp/message/location", {
        "to": to_number,
        "from": waba_number,
        "type": "location",
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "name": name,
            "address": address
        }
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_interactive_button_message(
    to_number: str,
    waba_number: str,
    body_text: str,
    buttons: list,
    header_text: str = "",
    footer_text: str = ""
) -> str:
    """
    Send a WhatsApp interactive message with clickable buttons.

    Args:
        to_number: Recipient phone number with country code
        waba_number: Your WhatsApp Business number
        body_text: Main message body text
        buttons: List of button dicts, each with 'id' and 'title' (max 3).
                 Example: [{"id": "yes_btn", "title": "Yes"}, {"id": "no_btn", "title": "No"}]
        header_text: Optional header text
        footer_text: Optional footer text
    """
    result = api_post("/whatsapp/message/interactive", {
        "to": to_number,
        "from": waba_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {"type": "text", "text": header_text} if header_text else None,
            "body": {"text": body_text},
            "footer": {"text": footer_text} if footer_text else None,
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                    for b in buttons
                ]
            }
        }
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def send_interactive_list_message(
    to_number: str,
    waba_number: str,
    body_text: str,
    button_label: str,
    sections: list,
    header_text: str = "",
    footer_text: str = ""
) -> str:
    """
    Send a WhatsApp interactive list message with a dropdown menu.

    Args:
        to_number: Recipient phone number with country code
        waba_number: Your WhatsApp Business number
        body_text: Main message body text
        button_label: Label on the button that opens the list (e.g. 'Choose Option')
        sections: List of section dicts. Each section has 'title' and 'rows'.
                  Each row has 'id', 'title', and optional 'description'.
                  Example: [{"title": "Plans", "rows": [{"id": "basic", "title": "Basic Plan", "description": "₹499/mo"}]}]
        header_text: Optional header text
        footer_text: Optional footer text
    """
    result = api_post("/whatsapp/message/interactive/list", {
        "to": to_number,
        "from": waba_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header_text} if header_text else None,
            "body": {"text": body_text},
            "footer": {"text": footer_text} if footer_text else None,
            "action": {"button": button_label, "sections": sections}
        }
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 💬 SECTION 2: CHAT MESSAGES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def export_chats_to_excel(
    customer_number: str,
    waba_number: str
) -> str:
    """
    Export all chat messages for a customer to Excel format.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
    """
    result = api_post("/whatsapp/chat/export", {
        "customerNumber": customer_number,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_chat_messages(
    customer_number: str,
    waba_number: str,
    page: int = 1,
    limit: int = 50
) -> str:
    """
    Get chat message history for a specific customer.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
        page: Page number for pagination (default: 1)
        limit: Number of messages per page (default: 50)
    """
    result = api_get("/whatsapp/chat/messages", params={
        "customerNumber": customer_number,
        "wabaNumber": waba_number,
        "page": page,
        "limit": limit
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 📢 SECTION 3: BROADCAST GROUPS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def send_broadcast_message(
    group_id: str,
    waba_number: str,
    template_name: str,
    language_code: str = "en",
    components: list = None
) -> str:
    """
    Send a WhatsApp template message to an entire broadcast group.

    Args:
        group_id: The ID of the broadcast group to send to
        waba_number: Your WhatsApp Business number
        template_name: Name of the approved template to use
        language_code: Language code (default: 'en')
        components: Optional list of component objects for dynamic variables
    """
    result = api_post("/whatsapp/broadcast/message", {
        "groupId": group_id,
        "wabaNumber": waba_number,
        "template": {
            "name": template_name,
            "language": {"code": language_code},
            "components": components or []
        }
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def create_broadcast_group(
    name: str,
    waba_number: str,
    members: list = None
) -> str:
    """
    Create a new broadcast group.

    Args:
        name: Name for the broadcast group (e.g. 'April Offer Campaign')
        waba_number: Your WhatsApp Business number
        members: Optional list of phone numbers to add immediately
    """
    result = api_post("/whatsapp/broadcast/group", {
        "name": name,
        "wabaNumber": waba_number,
        "members": members or []
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def delete_broadcast_groups(
    group_ids: list,
    waba_number: str
) -> str:
    """
    Delete one or more broadcast groups.

    Args:
        group_ids: List of group IDs to delete
        waba_number: Your WhatsApp Business number
    """
    result = api_delete("/whatsapp/broadcast/groups", {
        "groupIds": group_ids,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_broadcast_groups(
    waba_number: str,
    page: int = 1,
    limit: int = 20
) -> str:
    """
    Get a paginated list of all broadcast groups.

    Args:
        waba_number: Your WhatsApp Business number
        page: Page number (default: 1)
        limit: Groups per page (default: 20)
    """
    result = api_get("/whatsapp/broadcast/groups", params={
        "wabaNumber": waba_number,
        "page": page,
        "limit": limit
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def add_members_to_broadcast_group(
    group_id: str,
    waba_number: str,
    members: list
) -> str:
    """
    Add members (phone numbers) to an existing broadcast group.

    Args:
        group_id: The ID of the broadcast group
        waba_number: Your WhatsApp Business number
        members: List of phone numbers to add (with country code)
    """
    result = api_post("/whatsapp/broadcast/group/members", {
        "groupId": group_id,
        "wabaNumber": waba_number,
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
    waba_number: str,
    header_text: str = "",
    footer_text: str = "",
    buttons: list = None
) -> str:
    """
    Create a new WhatsApp message template (will be sent to Meta for approval).

    Args:
        name: Template name — lowercase, underscores only (e.g. 'order_confirmation')
        category: 'MARKETING', 'UTILITY', or 'AUTHENTICATION'
        language: Language code (e.g. 'en', 'hi', 'ta')
        body_text: Main body. Use {{1}}, {{2}} etc. for dynamic variables.
        waba_number: Your WhatsApp Business number
        header_text: Optional header text
        footer_text: Optional footer text (e.g. 'Reply STOP to unsubscribe')
        buttons: Optional list of button dicts
    """
    result = api_post("/whatsapp/template", {
        "name": name,
        "category": category,
        "language": language,
        "wabaNumber": waba_number,
        "components": [
            *([{"type": "HEADER", "format": "TEXT", "text": header_text}] if header_text else []),
            {"type": "BODY", "text": body_text},
            *([{"type": "FOOTER", "text": footer_text}] if footer_text else []),
            *([{"type": "BUTTONS", "buttons": buttons}] if buttons else []),
        ]
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def delete_template(
    template_name: str,
    waba_number: str
) -> str:
    """
    Delete a WhatsApp message template.

    Args:
        template_name: Name of the template to delete
        waba_number: Your WhatsApp Business number
    """
    result = api_delete("/whatsapp/template", {
        "name": template_name,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def edit_template(
    template_name: str,
    waba_number: str,
    body_text: str = "",
    footer_text: str = ""
) -> str:
    """
    Edit an existing WhatsApp template.

    Args:
        template_name: Name of the template to edit
        waba_number: Your WhatsApp Business number
        body_text: New body text (use {{1}}, {{2}} for variables)
        footer_text: New footer text
    """
    payload = {"name": template_name, "wabaNumber": waba_number}
    if body_text:
        payload["body"] = body_text
    if footer_text:
        payload["footer"] = footer_text
    result = api_patch("/whatsapp/template", payload)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_templates(waba_number: str) -> str:
    """
    Get all WhatsApp message templates for your account.

    Args:
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/template", params={"wabaNumber": waba_number})
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 👥 SECTION 5: CUSTOMER
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_customer_details(
    customer_number: str,
    waba_number: str
) -> str:
    """
    Get full details of a specific customer.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/customer", params={
        "customerNumber": customer_number,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def assign_tags_and_custom_fields(
    customer_number: str,
    waba_number: str,
    tags: list = None,
    custom_fields: dict = None
) -> str:
    """
    Assign tags and/or custom field values to a customer.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
        tags: List of tag strings to assign (e.g. ['Hot Lead', 'VIP'])
        custom_fields: Dict of custom field key-value pairs
                       (e.g. {'lead_stage': 'Prospect', 'city': 'Chennai'})
    """
    result = api_post("/whatsapp/customer/assign", {
        "customerNumber": customer_number,
        "wabaNumber": waba_number,
        "tags": tags or [],
        "customFields": custom_fields or {}
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def remove_tags_and_custom_fields(
    customer_number: str,
    waba_number: str,
    tags: list = None,
    custom_field_keys: list = None
) -> str:
    """
    Remove tags and/or custom fields from a customer.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
        tags: List of tag strings to remove (e.g. ['Hot Lead'])
        custom_field_keys: List of custom field keys to remove (e.g. ['lead_stage'])
    """
    result = api_post("/whatsapp/customer/remove", {
        "customerNumber": customer_number,
        "wabaNumber": waba_number,
        "tags": tags or [],
        "customFieldKeys": custom_field_keys or []
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def block_customer(
    customer_number: str,
    waba_number: str
) -> str:
    """
    Block a customer — they will no longer be able to send messages.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
    """
    result = api_post("/whatsapp/customer/block", {
        "customerNumber": customer_number,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def unblock_customer(
    customer_number: str,
    waba_number: str
) -> str:
    """
    Unblock a previously blocked customer.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
    """
    result = api_post("/whatsapp/customer/unblock", {
        "customerNumber": customer_number,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def check_reverted_on_time(
    customer_number: str,
    waba_number: str
) -> str:
    """
    Check if a customer reverted/replied within the SLA time window.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/customer/reverted-on-time", params={
        "customerNumber": customer_number,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def assign_team_member_to_customer(
    customer_number: str,
    waba_number: str,
    member_id: str
) -> str:
    """
    Assign a team member/agent to a specific customer.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
        member_id: ID of the team member to assign
    """
    result = api_post("/whatsapp/customer/assign-member", {
        "customerNumber": customer_number,
        "wabaNumber": waba_number,
        "memberId": member_id
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_chat_window_status(
    customer_number: str,
    waba_number: str
) -> str:
    """
    Check if the 24-hour chat window is open for a customer.
    (You can only send free-form messages within the 24hr window after customer's last message.)

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/customer/chat-window-status", params={
        "customerNumber": customer_number,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 👨‍💼 SECTION 6: TEAM MEMBER (CHAT ASSIGNMENT)
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def assign_team_member_to_chat(
    customer_number: str,
    waba_number: str,
    member_id: str
) -> str:
    """
    Assign a team member to handle a specific customer chat.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
        member_id: ID of the team member to assign
    """
    result = api_post("/whatsapp/chat/assign-member", {
        "customerNumber": customer_number,
        "wabaNumber": waba_number,
        "memberId": member_id
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def unassign_team_member_from_chat(
    customer_number: str,
    waba_number: str
) -> str:
    """
    Remove the team member assignment from a customer chat.

    Args:
        customer_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
    """
    result = api_post("/whatsapp/chat/unassign-member", {
        "customerNumber": customer_number,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def logout_team_member(member_id: str, waba_number: str) -> str:
    """
    Log out a team member from all their active devices.

    Args:
        member_id: ID of the team member to log out
        waba_number: Your WhatsApp Business number
    """
    result = api_post("/whatsapp/team/logout", {
        "memberId": member_id,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 💰 SECTION 7: WALLET
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_wallet_balance(waba_number: str) -> str:
    """
    Get the current wallet/credit balance for your JugaadX account.

    Args:
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/wallet/balance", params={"wabaNumber": waba_number})
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 👥 SECTION 8: TEAMS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_team(waba_number: str) -> str:
    """
    Get all team members in your JugaadX account.

    Args:
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/team", params={"wabaNumber": waba_number})
    return json.dumps(result, indent=2)


@mcp.tool()
def change_reporting_manager(
    member_id: str,
    manager_id: str,
    waba_number: str
) -> str:
    """
    Change the reporting manager for a team member.

    Args:
        member_id: ID of the team member
        manager_id: ID of the new reporting manager
        waba_number: Your WhatsApp Business number
    """
    result = api_patch("/whatsapp/team/reporting-manager", {
        "memberId": member_id,
        "managerId": manager_id,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def remove_team_member(member_id: str, waba_number: str) -> str:
    """
    Remove a team member from your JugaadX account.

    Args:
        member_id: ID of the team member to remove
        waba_number: Your WhatsApp Business number
    """
    result = api_delete("/whatsapp/team/member", {
        "memberId": member_id,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def add_member_under_reporting_manager(
    manager_id: str,
    member_id: str,
    waba_number: str
) -> str:
    """
    Add a team member under a specific reporting manager.

    Args:
        manager_id: ID of the reporting manager
        member_id: ID of the team member to place under this manager
        waba_number: Your WhatsApp Business number
    """
    result = api_post("/whatsapp/team/reporting-manager/member", {
        "managerId": manager_id,
        "memberId": member_id,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_team_member_details(member_id: str, waba_number: str) -> str:
    """
    Get full details of a specific team member.

    Args:
        member_id: ID of the team member
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/team/member", params={
        "memberId": member_id,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 🎭 SECTION 9: ROLES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_all_roles(waba_number: str) -> str:
    """
    Get all available roles and their permissions in your JugaadX account.

    Args:
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/roles", params={"wabaNumber": waba_number})
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 🖼️ SECTION 10: MEDIA
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def upload_media(
    file_url: str,
    media_type: str,
    waba_number: str
) -> str:
    """
    Upload a media file to JugaadX to get a media ID for use in messages.

    Args:
        file_url: Public URL of the media file to upload
        media_type: Type of media: 'image', 'video', 'audio', 'document'
        waba_number: Your WhatsApp Business number
    """
    result = api_post("/whatsapp/media/upload", {
        "fileUrl": file_url,
        "mediaType": media_type,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 🔔 SECTION 11: WEBHOOKS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def register_webhook(
    url: str,
    waba_number: str,
    triggers: list
) -> str:
    """
    Register a new webhook to receive real-time JugaadX events.

    Args:
        url: Your endpoint URL that will receive webhook POST requests
        waba_number: Your WhatsApp Business number
        triggers: List of event triggers to subscribe to. Available options:
                  'message_status_update' - when message status changes
                  'message_received'      - when a new message is received
                  'chat_assigned'         - when chat is assigned to agent
                  'chat_unassigned'       - when chat is unassigned
                  'lead_received_from_widget' - when lead from website widget
                  'first_time_message'    - customer's first message ever
                  'customer_custom_field_updated' - custom field changed
                  'template_updated'      - template status changed
                  'tag_added'             - tag added to conversation
                  'tag_removed'           - tag removed from conversation
    """
    result = api_post("/whatsapp/webhook", {
        "url": url,
        "wabaNumber": waba_number,
        "triggers": triggers
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_webhooks(waba_number: str) -> str:
    """
    Get all registered webhooks for your account.

    Args:
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/webhook", params={"wabaNumber": waba_number})
    return json.dumps(result, indent=2)


@mcp.tool()
def delete_webhooks(webhook_ids: list, waba_number: str) -> str:
    """
    Delete one or more registered webhooks.

    Args:
        webhook_ids: List of webhook IDs to delete
        waba_number: Your WhatsApp Business number
    """
    result = api_delete("/whatsapp/webhook", {
        "webhookIds": webhook_ids,
        "wabaNumber": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def edit_webhook(
    webhook_id: str,
    waba_number: str,
    url: str = "",
    triggers: list = None
) -> str:
    """
    Edit an existing webhook's URL or triggers.

    Args:
        webhook_id: ID of the webhook to edit
        waba_number: Your WhatsApp Business number
        url: New endpoint URL (leave empty to keep unchanged)
        triggers: New list of triggers (leave empty to keep unchanged)
    """
    payload = {"webhookId": webhook_id, "wabaNumber": waba_number}
    if url:
        payload["url"] = url
    if triggers:
        payload["triggers"] = triggers
    result = api_post("/whatsapp/webhook/edit", payload)
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 📞 SECTION 12: WHATSAPP CALLS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def create_outgoing_call(
    to_number: str,
    waba_number: str
) -> str:
    """
    Initiate an outgoing WhatsApp voice call to a customer.

    Args:
        to_number: Customer's phone number with country code
        waba_number: Your WhatsApp Business number
    """
    result = api_post("/whatsapp/call/outgoing", {
        "to": to_number,
        "from": waba_number
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def get_call_permissions(waba_number: str) -> str:
    """
    Check WhatsApp calling permissions for your account.

    Args:
        waba_number: Your WhatsApp Business number
    """
    result = api_get("/whatsapp/call/permissions", params={"wabaNumber": waba_number})
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════════════════════════════════
# 🚀 Run the server
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    print("🚀 JugaadX MCP Server starting...")
    print(f"📡 Base URL: {BASE_URL}")
    print(f"🔑 API Key: {'✅ Loaded' if JUGAADX_API_KEY != 'YOUR_API_KEY_HERE' else '❌ Not set!'}")
    print("🛠️  All tools ready!\n")
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = port
    mcp.run(transport="streamable-http")
