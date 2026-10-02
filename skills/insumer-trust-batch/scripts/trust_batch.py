#!/usr/bin/env python3
"""
Call POST /v1/trust/batch for multiple wallets in one request (max 10).

Reads INSUMER_API_KEY from env. Each successful wallet costs 3 credits (or 6
with merkle). Builds the proper array-of-objects request body.

Usage:
    python trust_batch.py --wallets 0xabc...,0xdef...
    python trust_batch.py --wallets-file allowlist.txt
    python trust_batch.py --wallets-file allowlist.txt --proof merkle

Wallet input formats:
    - --wallets: comma-separated EVM addresses (no per-wallet cross-chain fields)
    - --wallets-file: one EVM address per line, OR one JSON object per line for
      per-wallet cross-chain fields, e.g.:
          {"wallet":"0x...","solanaWallet":"5v9..."}
          {"wallet":"0x...","xrplWallet":"rN7n..."}
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

ENDPOINT = "https://api.insumermodel.com/v1/trust/batch"
MAX_WALLETS = 10


def parse_wallets_file(path: str) -> list:
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("{"):
                # JSON-line format with cross-chain fields
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON line: {line!r} — {e}", file=sys.stderr)
                    sys.exit(1)
                if "wallet" not in obj:
                    print(f"Missing 'wallet' in line: {line!r}", file=sys.stderr)
                    sys.exit(1)
                entries.append(obj)
            else:
                entries.append({"wallet": line})
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="POST /v1/trust/batch")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--wallets", help="Comma-separated EVM addresses")
    group.add_argument("--wallets-file", help="Path to file (one address or JSON obj per line)")
    parser.add_argument("--proof", choices=["merkle"],
                        help="Set 'merkle' for EIP-1186 proofs (6 credits/wallet)")
    args = parser.parse_args()

    api_key = os.environ.get("INSUMER_API_KEY")
    if not api_key:
        print("INSUMER_API_KEY not set. See the insumer-auth skill.", file=sys.stderr)
        return 1

    if args.wallets:
        entries = [{"wallet": w.strip()} for w in args.wallets.split(",") if w.strip()]
    else:
        entries = parse_wallets_file(args.wallets_file)

    if not entries:
        print("No wallets provided.", file=sys.stderr)
        return 1

    if len(entries) > MAX_WALLETS:
        print(f"Too many wallets ({len(entries)}). Max per call is {MAX_WALLETS}. "
              f"Batch client-side and call multiple times.", file=sys.stderr)
        return 1

    body_dict = {"wallets": entries}
    if args.proof:
        body_dict["proof"] = args.proof

    body = json.dumps(body_dict).encode("utf-8")

    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {err_body}", file=sys.stderr)
        return 1

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
