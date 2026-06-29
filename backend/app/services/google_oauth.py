"""
Verifies the Google ID token sent by the frontend's "Sign in with Google"
button. We use Google's tokeninfo endpoint via httpx so we don't need
the full google-auth library just for this one check.
"""
import httpx

from app.config import settings

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


def verify_google_token(id_token: str) -> dict | None:
    """
    Returns the decoded payload (email, name, sub/google_id) if valid,
    or None if the token is invalid / doesn't match our client id.
    """
    try:
        resp = httpx.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token}, timeout=10)
        if resp.status_code != 200:
            return None
        payload = resp.json()
        if payload.get("aud") != settings.GOOGLE_CLIENT_ID:
            return None
        return {
            "email": payload.get("email"),
            "name": payload.get("name", payload.get("email", "Google User")),
            "google_id": payload.get("sub"),
            "email_verified": payload.get("email_verified") == "true",
        }
    except Exception as exc:  # noqa: BLE001
        print(f"[google_oauth] verification failed: {exc}")
        return None
