# Review test cases

Eight cases for the plugin directory submission: five where the plugin should be used and three where it should not. Each is a prompt typed into ChatGPT with the InsumerAPI plugin installed, with the expected result. They are the cases entered in the review form, and the demo recording walks through them in this order.

The wallet used throughout is `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` (vitalik.eth), a public address whose state is well known: it holds ETH on Ethereum and is not an ERC-8004 agent.

## Positive cases

### P1. Signed attestation, condition met

**Prompt:** Use InsumerAPI to check whether wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 holds at least 1 ETH on Ethereum, and show me the attestation ID and signing key IDs.

**Expected:** `insumer_attest` is called with `chainId: 1`, `contractAddress: "native"`, `threshold: "1"`. The answer reports `met: true`, an attestation ID (`ATST-…`), `kid: insumer-attest-v2`, `pqKid: insumer-attest-pq1`. No balance figure appears anywhere.

### P2. Signed attestation, condition not met

**Prompt:** Use InsumerAPI to check whether wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 is a registered ERC-8004 agent with agent ID 1 on Base.

**Expected:** `insumer_attest` is called with `type: "erc8004_agent"`, `chainId: 8453`, `agentId: "1"`. The answer reports `met: false`, presented as a verdict (the wallet does not own or bind that agent), not as an error, with the attestation ID and key IDs.

### P3. Wallet trust profile

**Prompt:** Use InsumerAPI to build a wallet trust profile for 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 and summarize each dimension.

**Expected:** `insumer_wallet_trust` is called. The answer lists the ten dimensions with held / not-held counts, the profile ID (`TRST-…`), `conditionSetVersion`, and `kid: insumer-trust-v2`. It does not present a score or ranking, because the profile has none.

### P4. Public signing keys

**Prompt:** Use InsumerAPI to list its current signing keys and tell me how an attestation is verified offline.

**Expected:** `insumer_jwks` is called. The answer names the five key IDs (three ECDSA: `insumer-attest-v1`, `insumer-attest-v2`, `insumer-trust-v2`; two post-quantum: `insumer-attest-pq1`, `insumer-trust-pq1`), says to match keys by `kid` rather than position, and points at the `insumer-verify` package.

### P5. Merchant directory and discount check

**Prompt:** Use InsumerAPI to look up the merchant "skyemeta-demo-store" and tell me what discount wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 would get there.

**Expected:** `insumer_get_merchant` then `insumer_check_discount` are called. The answer gives the merchant's name (Skye Meta Demo Store) and tiers and the resulting discount percentage: 5% for a wallet that has not proven control, 10% if it does. No balance figure appears.

## Negative cases

In each of these the plugin should not be used.

### N1. Market price question

**Prompt:** What is the current price of ETH in USD?

**Expected:** No InsumerAPI tool is called. InsumerAPI does not provide market prices; the assistant answers from another source or says it cannot.

### N2. Request to send funds

**Prompt:** Send 0.5 ETH from my wallet to 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045.

**Expected:** No InsumerAPI tool is called and no transaction is sent. InsumerAPI reads wallet state and never sends a transaction.

### N3. A lost physical wallet

**Prompt:** I lost my wallet on the train yesterday. What should I do first, cancel my cards or file a police report?

**Expected:** No InsumerAPI tool is called. The question is about a physical wallet, not a blockchain address.

## Reviewer notes

- The hosted server needs no credentials. Reviewer credentials are therefore not required for the MCP connection; a free API key is only needed for the REST skills, and the review can be completed without one.
- The signed-result tools share a daily allowance across all users of the hosted server. If it is exhausted during review, the tools return a message saying so, which is itself the expected behaviour; it resets at 00:00 UTC.
- Every signed result in the recording can be checked independently: `npx insumer-verify` against the keys from case P4.
