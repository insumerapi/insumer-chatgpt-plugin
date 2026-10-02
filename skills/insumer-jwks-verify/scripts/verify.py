#!/usr/bin/env python3
"""
Verify an InsumerAPI signed response offline against the public JWKS.

Accepts either:
- A bare JWT string on stdin (when format: "jwt" was requested)
- A full response JSON object on stdin (uses the .jwt field if present)

Usage:
    echo "eyJhbGc..." | python verify.py
    echo '{"jwt":"eyJhbGc...","kid":"insumer-attest-v2"}' | python verify.py

Requires:
    pip install pyjwt[crypto]
"""
import json
import sys

try:
    import jwt
    from jwt import PyJWKClient
except ImportError:
    print("Missing dependency. Install with:\n    pip install 'pyjwt[crypto]'", file=sys.stderr)
    sys.exit(1)

JWKS_URL = "https://insumermodel.com/.well-known/jwks.json"
ISSUER = "https://api.insumermodel.com"
ALGORITHMS = ["ES256"]


def extract_jwt(stdin_text: str) -> str:
    stripped = stdin_text.strip()
    # Try parsing as JSON envelope first
    if stripped.startswith("{"):
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            return stripped
        # Look in common locations
        if isinstance(obj, dict):
            if "jwt" in obj:
                return obj["jwt"]
            if "data" in obj and isinstance(obj["data"], dict) and "jwt" in obj["data"]:
                return obj["data"]["jwt"]
        return stripped
    return stripped


def main() -> int:
    text = sys.stdin.read()
    if not text.strip():
        print("No input. Pipe a JWT or response JSON on stdin.", file=sys.stderr)
        return 1

    token = extract_jwt(text)
    if not token or "." not in token:
        print("INVALID: input does not look like a JWT.", file=sys.stderr)
        return 1

    jwks_client = PyJWKClient(JWKS_URL)
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=ALGORITHMS,
            issuer=ISSUER,
        )
    except jwt.InvalidIssuerError as e:
        print(f"INVALID: issuer mismatch — {e}", file=sys.stderr)
        return 1
    except jwt.ExpiredSignatureError:
        print("INVALID: JWT has expired (past its exp: 30 min, or 5 for a delegation condition).", file=sys.stderr)
        return 1
    except jwt.InvalidSignatureError:
        print("INVALID: signature does not verify against the public JWKS.", file=sys.stderr)
        return 1
    except jwt.PyJWTError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1

    print("OK")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
