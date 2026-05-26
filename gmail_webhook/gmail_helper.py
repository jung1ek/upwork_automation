from __future__ import annotations
import re
import base64

import base64
from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError

from logger import Logger

log = Logger().get_logger()


def fetch_thread_id(service) -> list[str]:
    """Given a Gmail API service and a historyId, fetch the associated thread IDs."""

    try:
        threads = (
            service.users().threads().list(
                userId="me",
                q=f"from:hello@upworkalerts.com",
                labelIds=["Label_3145636649811196972"],
                maxResults=1, # NOTE important, 1 means latest
            ).execute().get("threads", [])
        )
        log.info(f"Total threads in mailbox: {len(threads)}")
        return [thread["id"] for thread in threads]
    except Exception as e:
        log.error(f"Error fetching thread {e}")
        raise


def fetch_thread_data(service, thread_id: str) -> dict:
    """Fetch the full message data for a given thread ID."""

    try:
        thread = service.users().threads().get(userId="me", id=thread_id).execute()
        if "messages" not in thread or not thread["messages"]:
            raise ValueError(f"No messages found in thread {thread_id}")
        message = thread["messages"][0]["payload"]

        if message.get("mimeType") != "multipart/alternative":
            log.warning(f"Unexpected MIME type {message.get('mimeType')} in thread {thread_id}")
            return {}
        return extract_upwork_alert(message)
    except HttpError as e:
        log.error(f"Gmail API error fetching thread {thread_id}: {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error fetching thread {thread_id}: {e}")
        raise


def decode_part(data: str) -> str:
    """Decode a base64url Gmail body part, restoring stripped padding."""
    data = data.encode("utf-8") if isinstance(data, str) else data
    data += b"=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")


def extract_upwork_alert(payload: dict) -> dict:
    """
    Parse an UpworkAlerts email payload into structured fields.
    Prefers text/plain for body parsing; falls back to text/html.
    """
    # 1. Pull headers
    headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}

    # 2. Find parts by mimeType 
    parts      = payload.get("parts", [])
    html_part  = next((p for p in parts if p["mimeType"] == "text/html"),  None)

    # 3. parse html
    html_text  = decode_part(html_part["body"]["data"])  if html_part  else ""

    # 4. Parse structured fields from html text
    job = parse_html_body(html_text) if html_text else {}

    return {
        # envelope
        "message_id":   headers.get("message-id", ""),
        "from":         headers.get("from", ""),
        "to":           headers.get("to", ""),
        "subject":      headers.get("subject", ""),
        "date":         headers.get("date", ""),
        # authentication — quick pass/fail summary
        "dkim":         "pass" if "dkim=pass"  in headers.get("authentication-results", "") else "fail",
        "spf":          "pass" if "spf=pass"   in headers.get("authentication-results", "") else "fail",
        "dmarc":        "pass" if "dmarc=pass" in headers.get("authentication-results", "") else "fail",
        # job fields
        **job,
    }


def parse_html_body(html: str) -> dict:
    """
    Parse text/html part of an UpworkAlerts email.
    Targets stable class names and structural patterns, not brittle CSS values.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Job title 
    # Only <p> with font-size:20px in the email-body section
    title = ""
    email_body = soup.find("td", class_="email-body")
    if email_body:
        p = email_body.find("p", style=re.compile(r"font-size:20px"))
        if p:
            title = p.get_text(strip=True)

    # Description 
    # Only <p> with line-height:1.7
    description = ""
    if email_body:
        p = email_body.find("p", style=re.compile(r"line-height:1\.7"))
        if p:
            description = p.get_text(strip=True)

    # Budget & Client rating (pill cards) 
    # Each card: uppercase label <p> + bold value <p> inside a stack-cell td
    budget = client_rating = ""
    for cell in soup.find_all("td", class_="stack-cell"):
        label_p = cell.find("p", style=re.compile(r"text-transform:uppercase"))
        value_p = cell.find("p", style=re.compile(r"font-weight:bold"))
        if label_p and value_p:
            label = label_p.get_text(strip=True).lower()
            value = value_p.get_text(strip=True)
            if label == "budget":
                budget = value
            elif label == "client rating":
                client_rating = value

    # sClient overview chips 
    # Each chip-pill span: <span style="font-weight:bold">VALUE</span> LABEL
    chips = {}
    for chip in soup.find_all("span", class_="chip-pill"):
        bold = chip.find("span", style=re.compile(r"font-weight:bold"))
        if not bold:
            continue
        value = bold.get_text(strip=True)

        # Label = text node after the bold span (strip whitespace)
        label = chip.get_text(strip=True).replace(value, "").strip().lower()
        chips[label] = value

    # Keyword match tags 
    keywords = [
        td.get_text(strip=True)
        for td in soup.find_all("td", style=re.compile(r"#EAF3DE"))
        if td.get_text(strip=True) not in ("🔍", "")
    ]

    # CTA URLs
    apply_url = view_url = ""
    for a in soup.find_all("a", class_="cta-link"):
        label = a.get_text(strip=True).lower()
        href  = a.get("href", "")
        if label == "apply now":
            apply_url = href
        elif label == "view job":
            view_url = href
    
    # ── Job ID — extract from view_url or apply_url ───────────────────────
    job_id = ""
    for url in (apply_url, view_url):
        m = re.search(r"~(\d+)", url)
        if m:
            job_id = m.group(1)   # "022056925938890446135"
            break

    return {
        "job_id": job_id,
        "job_title":     title,
        "description":   description,
        "budget":        budget,
        "client_rating": client_rating,
        "location":      chips.get("client location", ""),
        "hire_rate":     chips.get("hire rate", ""),
        "total_spent":   chips.get("total spent", ""),
        "avg_rate":      chips.get("avg. paid", ""),
        "hires":         chips.get("hires", ""),
        "open_jobs":     chips.get("jobs", ""),
        "member_since":  chips.get("member since", ""),
        "keywords":      keywords,
        "apply_url":     apply_url,
        "view_url":      view_url,
        "source":        "text/html",
    }

