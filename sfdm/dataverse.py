"""Thin client for the Dataverse Web API (the API behind Dynamics 365).

Two sign-in options, picked automatically from your .env:
  * CLIENT_SECRET set   -> app registration (client credentials) - best for automation
  * CLIENT_SECRET blank -> device-code sign-in with your own trial user - easiest to start
"""

from __future__ import annotations

import re
import time
import uuid

from . import config

# Microsoft's published sample client id for Dataverse development/testing.
# Fine for a trial; register your own app for anything real.
SAMPLE_PUBLIC_CLIENT_ID = "51f81489-12ee-4a9e-aaae-a2591f45987d"
TOKEN_CACHE = config.ROOT / ".token_cache.bin"
GUID_RE = re.compile(r"\(([0-9a-fA-F-]{36})\)")


class DataverseClient:
    def __init__(self, url: str, token: str):
        import requests

        self.base = url.rstrip("/") + "/api/data/v9.2/"
        self.http = requests.Session()
        self.http.headers.update({
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        })

    # -- plumbing -----------------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs):
        for attempt in range(5):
            resp = self.http.request(method, self.base + path, timeout=60, **kwargs)
            if resp.status_code == 429:  # Dataverse service-protection limit
                time.sleep(int(resp.headers.get("Retry-After", 2 ** attempt)))
                continue
            if resp.status_code >= 400:
                raise RuntimeError(f"{method} {path} -> {resp.status_code}: {resp.text[:400]}")
            return resp
        raise RuntimeError(f"{method} {path} kept hitting the API rate limit")

    # -- operations used by the loader -------------------------------------------
    def find_by_key(self, entity_set: str, pk: str, key_column: str, key: str) -> str | None:
        safe = key.replace("'", "''")
        resp = self._request("GET", f"{entity_set}?$select={pk}&$filter={key_column} eq '{safe}'")
        rows = resp.json().get("value", [])
        return rows[0][pk] if rows else None

    def create(self, entity_set: str, payload: dict) -> str:
        resp = self._request("POST", entity_set, json=payload)
        match = GUID_RE.search(resp.headers.get("OData-EntityId", ""))
        if not match:
            raise RuntimeError(f"Created {entity_set} record but no id came back")
        return match.group(1)

    def update(self, entity_set: str, guid: str, payload: dict) -> None:
        self._request("PATCH", f"{entity_set}({guid})", json=payload)

    def count_migrated(self, entity_set: str, pk: str, key_column: str) -> int:
        resp = self._request(
            "GET", f"{entity_set}?$select={pk}&$filter={key_column} ne null&$count=true",
            headers={"Prefer": "odata.maxpagesize=1"},
        )
        return int(resp.json().get("@odata.count", 0))


class DryRunClient:
    """Same interface, no network. Lets anyone run the full pipeline on sample data."""

    def __init__(self):
        self.tables: dict[str, dict[str, dict]] = {}

    def find_by_key(self, entity_set, pk, key_column, key):
        for guid, row in self.tables.get(entity_set, {}).items():
            if row.get(key_column) == key:
                return guid
        return None

    def create(self, entity_set, payload):
        guid = str(uuid.uuid4())
        self.tables.setdefault(entity_set, {})[guid] = dict(payload)
        return guid

    def update(self, entity_set, guid, payload):
        self.tables[entity_set][guid].update(payload)

    def count_migrated(self, entity_set, pk, key_column):
        return sum(1 for r in self.tables.get(entity_set, {}).values() if r.get(key_column))


def get_token(url: str) -> str:
    import msal

    scope = [url.rstrip("/") + "/.default"]
    tenant = config.env("TENANT_ID", required=False) or "organizations"
    authority = f"https://login.microsoftonline.com/{tenant}"
    secret = config.env("CLIENT_SECRET", required=False)

    if secret:
        app = msal.ConfidentialClientApplication(
            config.env("CLIENT_ID"), authority=authority, client_credential=secret)
        result = app.acquire_token_for_client(scopes=scope)
    else:
        cache = msal.SerializableTokenCache()
        if TOKEN_CACHE.exists():
            cache.deserialize(TOKEN_CACHE.read_text())
        app = msal.PublicClientApplication(
            config.env("CLIENT_ID", required=False) or SAMPLE_PUBLIC_CLIENT_ID,
            authority=authority, token_cache=cache)
        accounts = app.get_accounts()
        result = app.acquire_token_silent(scope, account=accounts[0]) if accounts else None
        if not result:
            flow = app.initiate_device_flow(scopes=scope)
            print("\n" + flow["message"] + "\n")   # "go to microsoft.com/devicelogin and enter code ..."
            result = app.acquire_token_by_device_flow(flow)
        if cache.has_state_changed:
            TOKEN_CACHE.write_text(cache.serialize())

    if "access_token" not in result:
        raise SystemExit(f"Sign-in failed: {result.get('error_description', result)}")
    return result["access_token"]


def connect(dry_run: bool = False):
    if dry_run:
        return DryRunClient()
    config.load_env()
    url = config.env("DATAVERSE_URL")
    return DataverseClient(url, get_token(url))
